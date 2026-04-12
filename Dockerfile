# ── Stage 1: Build ────────────────────────────────────────────────
FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /build

# Cache dependencies first (only re-downloads when pom.xml changes)
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy source and build the fat JAR
COPY src ./src
RUN mvn package -DskipTests -B

# ── Stage 2: Run ─────────────────────────────────────────────────
FROM eclipse-temurin:17-jre-jammy

WORKDIR /app

# Copy the built JAR
COPY --from=builder /build/target/*.jar app.jar

# Create temp dir for code execution workspace
RUN mkdir -p /tmp/codex/submissions

EXPOSE 8080

# JVM sizing for 1GB EC2 (shared with executor agent)
#   OS ~80MB, Docker ~40MB, Other services ~150MB
#   Leave only 130MB for backend JVM (executor agent gets 100MB)
ENTRYPOINT ["java", \
  "-Xms32m", "-Xmx130m", \
  "-XX:+UseContainerSupport", \
  "-XX:MaxRAMPercentage=60.0", \
  "-Duser.timezone=UTC", \
  "-Dspring.profiles.active=prod", \
  "-jar", "app.jar"]
