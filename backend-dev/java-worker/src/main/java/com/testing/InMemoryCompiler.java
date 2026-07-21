package com.testing;

import javax.tools.*;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.URI;
import java.util.*;

public class InMemoryCompiler {

    private static final JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
    private static final StandardJavaFileManager standardFileManager;

    static {
        if (compiler == null) {
            throw new RuntimeException("JavaCompiler is null. Make sure you are running with a JDK, not a JRE.");
        }
        standardFileManager = compiler.getStandardFileManager(null, null, null);
        try {
            List<java.io.File> classpath = new ArrayList<>();
            String[] classpathEntries = System.getProperty("java.class.path").split(java.io.File.pathSeparator);
            for (String entry : classpathEntries) {
                classpath.add(new java.io.File(entry));
            }
            standardFileManager.setLocation(StandardLocation.CLASS_PATH, classpath);
        } catch (java.io.IOException e) {
            e.printStackTrace();
        }
    }

    public static Map<String, byte[]> compile(Map<String, String> sources) throws Exception {
        if (compiler == null) {
            throw new RuntimeException("JavaCompiler is null. Make sure you are running with a JDK, not a JRE.");
        }
        DiagnosticCollector<JavaFileObject> diagnostics = new DiagnosticCollector<>();
        InMemoryFileManager fileManager = new InMemoryFileManager(standardFileManager);

        List<JavaFileObject> compilationUnits = new ArrayList<>();
        for (Map.Entry<String, String> entry : sources.entrySet()) {
            compilationUnits.add(new StringJavaFileObject(entry.getKey(), entry.getValue()));
        }

        // Empty options since classpath is already cached in fileManager
        List<String> options = new ArrayList<>();

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
