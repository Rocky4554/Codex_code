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

# JVM sizing for Northflank 512MB container
#   OS ~80MB, Hikari pool (5 conns) ~30MB, Redisson ~40MB
#   Leaves ~300MB for the JVM heap
ENTRYPOINT ["java", \
  "-Xms64m", "-Xmx300m", \
  "-XX:+UseContainerSupport", \
  "-XX:MaxRAMPercentage=60.0", \
  "-Duser.timezone=UTC", \
  "-jar", "app.jar"]
