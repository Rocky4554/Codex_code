# ── Stage 1: Build ────────────────────────────────────────────────
FROM maven:3.9-eclipse-temurin-17-jammy AS builder

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

# JVM sizing for EC2 t2.small (2 GB RAM)
#   Redis ~50MB, OS ~300MB, code-exec containers ~256MB each
#   Leaves ~400MB for the JVM
ENTRYPOINT ["java", \
  "-Xms128m", "-Xmx384m", \
  "-Duser.timezone=UTC", \
  "-jar", "app.jar"]
