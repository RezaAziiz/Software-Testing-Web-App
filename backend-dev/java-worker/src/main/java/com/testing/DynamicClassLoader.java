package com.testing;

import org.jacoco.core.instr.Instrumenter;
import org.jacoco.core.runtime.IRuntime;
import java.util.Map;
import java.util.HashMap;

public class DynamicClassLoader extends ClassLoader {
    private final Map<String, byte[]> classes;
    private final Map<String, Class<?>> loadedClasses = new HashMap<>();
    private final Instrumenter instrumenter;

    public DynamicClassLoader(Map<String, byte[]> classes, IRuntime runtime, ClassLoader parent) {
        super(parent);
        this.classes = classes;
        this.instrumenter = new Instrumenter(runtime);
    }

    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        if (loadedClasses.containsKey(name)) {
            return loadedClasses.get(name);
        }

        byte[] b = classes.get(name);
        if (b == null) {
            return super.findClass(name);
        }

        try {
            // Instrument the class bytes with JaCoCo hooks
            byte[] instrumented = instrumenter.instrument(b, name);
            Class<?> clazz = defineClass(name, instrumented, 0, instrumented.length);
            loadedClasses.put(name, clazz);
            return clazz;
        } catch (Exception e) {
            throw new ClassNotFoundException("Failed to instrument class " + name, e);
        }
    }
}
