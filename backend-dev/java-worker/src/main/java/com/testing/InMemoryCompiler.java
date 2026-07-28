package com.testing;

import javax.tools.*;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.net.URI;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.*;

public class InMemoryCompiler {

    private static final JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
    // Cache classpath string once (immutable, thread-safe)
    private static final String cachedClasspath;

    static {
        if (compiler == null) {
            throw new RuntimeException("JavaCompiler is null. Make sure you are running with a JDK, not a JRE.");
        }
        cachedClasspath = buildClasspathString();
    }

    private static List<File> buildClasspathFiles() {
        Set<String> pathStrings = new LinkedHashSet<>();
        
        // 1. System property java.class.path
        String sysCp = System.getProperty("java.class.path");
        if (sysCp != null) {
            for (String p : sysCp.split(File.pathSeparator)) {
                if (!p.trim().isEmpty()) {
                    pathStrings.add(p.trim());
                }
            }
        }
        
        // 2. ClassLoader hierarchy (handles Maven ClassWorlds / URLClassLoader)
        ClassLoader cl = Thread.currentThread().getContextClassLoader();
        while (cl != null) {
            if (cl instanceof URLClassLoader) {
                for (URL url : ((URLClassLoader) cl).getURLs()) {
                    try {
                        File f = new File(url.toURI());
                        pathStrings.add(f.getAbsolutePath());
                    } catch (Exception ignored) {}
                }
            }
            cl = cl.getParent();
        }

        List<File> files = new ArrayList<>();
        for (String p : pathStrings) {
            files.add(new File(p));
        }
        return files;
    }

    private static String buildClasspathString() {
        StringBuilder sb = new StringBuilder();
        for (File f : buildClasspathFiles()) {
            if (sb.length() > 0) sb.append(File.pathSeparator);
            sb.append(f.getAbsolutePath());
        }
        return sb.toString();
    }

    public static Map<String, byte[]> compile(Map<String, String> sources) throws Exception {
        if (compiler == null) {
            throw new RuntimeException("JavaCompiler is null. Make sure you are running with a JDK, not a JRE.");
        }
        
        // Create a fresh StandardJavaFileManager per call (NOT thread-safe if shared)
        StandardJavaFileManager stdFileManager = compiler.getStandardFileManager(null, null, null);
        
        DiagnosticCollector<JavaFileObject> diagnostics = new DiagnosticCollector<>();
        InMemoryFileManager fileManager = new InMemoryFileManager(stdFileManager);

        List<JavaFileObject> compilationUnits = new ArrayList<>();
        for (Map.Entry<String, String> entry : sources.entrySet()) {
            compilationUnits.add(new StringJavaFileObject(entry.getKey(), entry.getValue()));
        }

        List<String> options = new ArrayList<>();
        options.add("-classpath");
        options.add(cachedClasspath);

        JavaCompiler.CompilationTask task = compiler.getTask(null, fileManager, diagnostics, options, null, compilationUnits);

        boolean success = task.call();
        if (!success) {
            StringBuilder errorMsg = new StringBuilder();
            for (Diagnostic<? extends JavaFileObject> diagnostic : diagnostics.getDiagnostics()) {
                errorMsg.append(diagnostic.toString()).append("\n");
            }
            throw new Exception("Compilation failed:\n" + errorMsg);
        }

        return fileManager.getCompiledClasses();
    }

    private static class StringJavaFileObject extends SimpleJavaFileObject {
        private final String code;

        protected StringJavaFileObject(String className, String code) {
            super(URI.create("string:///" + className.replace('.', '/') + Kind.SOURCE.extension), Kind.SOURCE);
            this.code = code;
        }

        @Override
        public CharSequence getCharContent(boolean ignoreEncodingErrors) {
            return code;
        }
    }

    private static class InMemoryFileManager extends ForwardingJavaFileManager<StandardJavaFileManager> {
        private final Map<String, ByteArrayJavaFileObject> compiledClasses = new HashMap<>();

        protected InMemoryFileManager(StandardJavaFileManager fileManager) {
            super(fileManager);
        }

        @Override
        public JavaFileObject getJavaFileForOutput(Location location, String className, JavaFileObject.Kind kind, FileObject sibling) {
            ByteArrayJavaFileObject file = new ByteArrayJavaFileObject(className);
            compiledClasses.put(className, file);
            return file;
        }

        public Map<String, byte[]> getCompiledClasses() {
            Map<String, byte[]> result = new HashMap<>();
            for (Map.Entry<String, ByteArrayJavaFileObject> entry : compiledClasses.entrySet()) {
                result.put(entry.getKey(), entry.getValue().getBytes());
            }
            return result;
        }
    }

    private static class ByteArrayJavaFileObject extends SimpleJavaFileObject {
        private final ByteArrayOutputStream baos = new ByteArrayOutputStream();

        protected ByteArrayJavaFileObject(String className) {
            super(URI.create("bytes:///" + className.replace('.', '/') + Kind.CLASS.extension), Kind.CLASS);
        }

        @Override
        public OutputStream openOutputStream() throws IOException {
            return baos;
        }

        public byte[] getBytes() {
            return baos.toByteArray();
        }
    }
}
