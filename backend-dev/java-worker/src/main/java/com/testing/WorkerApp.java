package com.testing;

import io.javalin.Javalin;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.HashMap;

public class WorkerApp {
    private static final Logger logger = LoggerFactory.getLogger(WorkerApp.class);
    private static final ObjectMapper mapper = new ObjectMapper();
    private static final ExecutionService executionService = new ExecutionService();

    public static void main(String[] args) {
        int port = 8081;
        String envPort = System.getenv("PORT");
        if (envPort != null && !envPort.isEmpty()) {
            try {
                port = Integer.parseInt(envPort);
            } catch (NumberFormatException e) {
                logger.warn("Invalid PORT environment variable, falling back to 8081");
            }
        }

        Javalin app = Javalin.create(config -> {
            config.showJavalinBanner = false;
            // Increase HTTP request timeout for load testing (500 concurrent users waiting on semaphore)
            config.http.maxRequestSize = 10_000_000L;
        }).start(port);

        app.post("/execute", ctx -> {
            try {
                String body = ctx.body();
                JsonNode json = mapper.readTree(body);

                String mainClassName = json.get("mainClassName").asText();
                String mainCode = json.get("mainCode").asText();
                String testClassName = json.get("testClassName").asText();
                String testCode = json.get("testCode").asText();
                
                String reportOutputDir = null;
                if (json.has("reportOutputDir")) {
                    reportOutputDir = json.get("reportOutputDir").asText();
                }

                logger.info("Received execution request for {}", mainClassName);

                // Execute
                Map<String, Object> result = executionService.runTest(mainClassName, mainCode, testClassName, testCode, reportOutputDir);

                ctx.json(result);
            } catch (Exception e) {
                ctx.status(500);
                Map<String, String> error = new HashMap<>();
                error.put("error", e.getMessage());
                ctx.json(error);
            }
        });

        app.post("/compile", ctx -> {
            try {
                String body = ctx.body();
                JsonNode json = mapper.readTree(body);

                String mainClassName = json.get("mainClassName").asText();
                String mainCode = json.get("mainCode").asText();
                
                Map<String, Object> result = executionService.compileOnly(mainClassName, mainCode);
                ctx.json(result);
            } catch (Exception e) {
                ctx.status(500);
                Map<String, String> error = new HashMap<>();
                error.put("error", e.getMessage());
                ctx.json(error);
            }
        });
        
        logger.info("Java Executor Worker started on port 8081");
    }
}
