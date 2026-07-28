package com.testing;

import org.jacoco.core.analysis.Analyzer;
import org.jacoco.core.analysis.CoverageBuilder;
import org.jacoco.core.analysis.IClassCoverage;
import org.jacoco.core.analysis.ICounter;
import org.jacoco.core.analysis.ILine;
import org.jacoco.core.data.ExecutionDataStore;
import org.jacoco.core.data.SessionInfoStore;
import org.jacoco.core.runtime.IRuntime;
import org.jacoco.core.runtime.LoggerRuntime;
import org.jacoco.core.runtime.RuntimeData;
import org.jacoco.report.FileMultiReportOutput;
import org.jacoco.report.IReportVisitor;
import org.jacoco.report.ISourceFileLocator;
import org.jacoco.report.html.HTMLFormatter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Base64;
import java.io.ByteArrayOutputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import org.junit.platform.engine.discovery.DiscoverySelectors;
import org.junit.platform.launcher.Launcher;
import org.junit.platform.launcher.LauncherDiscoveryRequest;
import org.junit.platform.launcher.core.LauncherDiscoveryRequestBuilder;
import org.junit.platform.launcher.core.LauncherFactory;
import org.junit.platform.launcher.listeners.SummaryGeneratingListener;
import org.junit.platform.launcher.listeners.TestExecutionSummary;

import java.io.File;
import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;
import java.util.*;

public class ExecutionService {

    private static final Launcher launcher = org.junit.platform.launcher.core.LauncherFactory.create();
    
    // Limit concurrent executions to CPU core count to prevent CPU thrashing
    private static final int MAX_CONCURRENT = Runtime.getRuntime().availableProcessors();
    private static final java.util.concurrent.Semaphore executionSemaphore = new java.util.concurrent.Semaphore(MAX_CONCURRENT);
    
    static {
        System.out.println("ExecutionService: max concurrent executions = " + MAX_CONCURRENT + " (CPU cores)");
    }

    public Map<String, Object> runTest(String mainClassName, String mainCode, String testClassName, String testCode, String reportOutputDir) throws Exception {
        long waitStart = System.currentTimeMillis();
        executionSemaphore.acquire();
        long waitTime = System.currentTimeMillis() - waitStart;
        
        try {
            return doRunTest(mainClassName, mainCode, testClassName, testCode, reportOutputDir, waitTime);
        } finally {
            executionSemaphore.release();
        }
    }
    
    private Map<String, Object> doRunTest(String mainClassName, String mainCode, String testClassName, String testCode, String reportOutputDir, long semaphoreWaitMs) throws Exception {
        Map<String, Object> result = new HashMap<>();
        long t0 = System.currentTimeMillis();
        if (semaphoreWaitMs > 10) {
            System.out.println("Waited " + semaphoreWaitMs + "ms in queue for " + mainClassName);
        }
        
        // 1. Compile In-Memory
        Map<String, String> sources = new HashMap<>();
        sources.put(mainClassName, mainCode);
        sources.put(testClassName, testCode);
        
        Map<String, byte[]> compiledClasses = InMemoryCompiler.compile(sources);
        long t1 = System.currentTimeMillis();
        System.out.println("Time to compile: " + (t1 - t0) + "ms");
        
        // 2. Setup JaCoCo Runtime
        IRuntime runtime = new LoggerRuntime();
        RuntimeData data = new RuntimeData();
        runtime.startup(data);
        long t2 = System.currentTimeMillis();
        System.out.println("Time to startup JaCoCo: " + (t2 - t1) + "ms");

        // 3. Setup Custom ClassLoader & Inject JaCoCo
        DynamicClassLoader classLoader = new DynamicClassLoader(compiledClasses, runtime, getClass().getClassLoader());
        long t3 = System.currentTimeMillis();
        System.out.println("Time to create classloader: " + (t3 - t2) + "ms");
        
        // 4. Run JUnit 5
        ClassLoader originalClassLoader = Thread.currentThread().getContextClassLoader();
        Thread.currentThread().setContextClassLoader(classLoader);
        try {
            Class<?> testClass = classLoader.loadClass(testClassName);
            long t4 = System.currentTimeMillis();
            System.out.println("Time to load classes: " + (t4 - t3) + "ms");
            
            LauncherDiscoveryRequest request = LauncherDiscoveryRequestBuilder.request()
                .selectors(DiscoverySelectors.selectClass(testClass))
                .build();
                
            SummaryGeneratingListener listener = new SummaryGeneratingListener();
            long t5 = System.currentTimeMillis();
            launcher.execute(request, listener);
            long t6 = System.currentTimeMillis();
            System.out.println("Time to execute tests: " + (t6 - t5) + "ms");
            
            TestExecutionSummary summary = listener.getSummary();
            result.put("totalTests", summary.getTestsFoundCount());
            result.put("passedTests", summary.getTestsSucceededCount());
            result.put("failedTests", summary.getTestsFailedCount());
            result.put("isAllPassed", summary.getTestsFailedCount() == 0 && summary.getTestsSucceededCount() > 0);
            
            // Extract failures
            List<Map<String, String>> failures = new ArrayList<>();
            for (TestExecutionSummary.Failure failure : summary.getFailures()) {
                Map<String, String> f = new HashMap<>();
                f.put("testName", failure.getTestIdentifier().getDisplayName());
                f.put("message", failure.getException().getMessage());
                failures.add(f);
            }
            result.put("failures", failures);
            
        } finally {
            Thread.currentThread().setContextClassLoader(originalClassLoader);
            runtime.shutdown();
        }
        
        long t7 = System.currentTimeMillis();
        // 5. Collect Execution Data
        ExecutionDataStore executionData = new ExecutionDataStore();
        SessionInfoStore sessionInfos = new SessionInfoStore();
        data.collect(executionData, sessionInfos, false);
        
        // 6. Analyze Coverage
        CoverageBuilder coverageBuilder = new CoverageBuilder();
        Analyzer analyzer = new Analyzer(executionData, coverageBuilder);
        
        for (Map.Entry<String, byte[]> entry : compiledClasses.entrySet()) {
            // Only analyze the main class (skip test class coverage)
            if (entry.getKey().equals(mainClassName)) {
                analyzer.analyzeClass(entry.getValue(), entry.getKey());
            }
        }
        long t8 = System.currentTimeMillis();
        System.out.println("Time to analyze coverage: " + (t8 - t7) + "ms");
        
        // 7. Extract Line Coverage Status for CFG Node Coloring
        List<Map<String, Object>> lineStatuses = new ArrayList<>();
        double coveragePercent = 0.0;
        
        for (IClassCoverage cc : coverageBuilder.getClasses()) {
            // FIX: Use Instruction Counter instead of Method Counter for accurate coverage percent
            int covered = cc.getInstructionCounter().getCoveredCount();
            int total = cc.getInstructionCounter().getTotalCount();
            if (total > 0) {
                coveragePercent = ((double) covered / total) * 100.0;
            }
            
            for (int i = cc.getFirstLine(); i <= cc.getLastLine(); i++) {
                ILine line = cc.getLine(i);
                if (line.getStatus() != ICounter.EMPTY) {
                    Map<String, Object> ls = new HashMap<>();
                    ls.put("line", i);
                    String statusStr = "NOT_COVERED";
                    if (line.getStatus() == ICounter.FULLY_COVERED) statusStr = "FULLY_COVERED";
                    else if (line.getStatus() == ICounter.PARTLY_COVERED) statusStr = "PARTLY_COVERED";
                    ls.put("status", statusStr);
                    lineStatuses.add(ls);
                }
            }
        }
        
        // 8. Generate JaCoCo HTML Report (if requested)
        if (reportOutputDir != null && !reportOutputDir.isEmpty()) {
            java.io.File reportDir = Files.createTempDirectory("jacoco-report").toFile();
            
            HTMLFormatter htmlFormatter = new HTMLFormatter();
            IReportVisitor visitor = htmlFormatter.createVisitor(new FileMultiReportOutput(reportDir));
            
            visitor.visitInfo(sessionInfos.getInfos(), executionData.getContents());
            
            // Custom Source File Locator for In-Memory String Code
            ISourceFileLocator sourceLocator = new ISourceFileLocator() {
                @Override
                public java.io.Reader getSourceFile(String packageName, String fileName) throws java.io.IOException {
                    if (fileName.equals(mainClassName + ".java")) {
                        return new java.io.StringReader(mainCode);
                    }
                    return null;
                }
                @Override
                public int getTabWidth() {
                    return 4;
                }
            };
            
            visitor.visitBundle(coverageBuilder.getBundle("Coverage_Report"), sourceLocator);
            visitor.visitEnd();

            // Only read the single source HTML file (the only unique file per execution)
            java.io.File sourceHtml = new java.io.File(reportDir, "default/" + mainClassName + ".java.html");
            if (sourceHtml.exists()) {
                result.put("sourceHtmlContent", new String(Files.readAllBytes(sourceHtml.toPath()), java.nio.charset.StandardCharsets.UTF_8));
            }
            
            // Cleanup temp directory
            deleteDirectory(reportDir);
        }
        
        result.put("coveragePercent", coveragePercent);
        result.put("lineStatuses", lineStatuses);
        result.put("semaphoreWaitMs", semaphoreWaitMs);
        result.put("totalExecutionMs", System.currentTimeMillis() - t0);
        
        return result;
    }

    public Map<String, Object> compileOnly(String mainClassName, String mainCode) {
        Map<String, Object> result = new HashMap<>();
        try {
            Map<String, String> sources = new HashMap<>();
            sources.put(mainClassName, mainCode);
            InMemoryCompiler.compile(sources);
            
            result.put("success", true);
            result.put("message", "Compilation successful");
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", e.getMessage());
        }
        return result;
    }

    private String zipDirectoryToBase64(java.io.File dir) throws java.io.IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        try (ZipOutputStream zos = new ZipOutputStream(baos)) {
            Path sourcePath = dir.toPath();
            Files.walk(sourcePath)
                .filter(path -> !Files.isDirectory(path))
                .forEach(path -> {
                    ZipEntry zipEntry = new ZipEntry(sourcePath.relativize(path).toString().replace("\\", "/"));
                    try {
                        zos.putNextEntry(zipEntry);
                        Files.copy(path, zos);
                        zos.closeEntry();
                    } catch (java.io.IOException e) {
                        e.printStackTrace();
                    }
                });
        }
        return Base64.getEncoder().encodeToString(baos.toByteArray());
    }

    private void deleteDirectory(java.io.File directoryToBeDeleted) {
        java.io.File[] allContents = directoryToBeDeleted.listFiles();
        if (allContents != null) {
            for (java.io.File file : allContents) {
                deleteDirectory(file);
            }
        }
        directoryToBeDeleted.delete();
    }
}
