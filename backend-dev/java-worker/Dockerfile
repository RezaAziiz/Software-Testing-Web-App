FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jdk-jammy
WORKDIR /app
COPY --from=builder /app/target/java-worker-1.0-SNAPSHOT-jar-with-dependencies.jar ./java-worker.jar

ENV PORT=8081
EXPOSE 8081

CMD ["java", "-jar", "java-worker.jar"]
