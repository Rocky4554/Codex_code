package com.codex.platform.config;

import com.github.dockerjava.api.DockerClient;
import com.github.dockerjava.core.DefaultDockerClientConfig;
import com.github.dockerjava.core.DockerClientImpl;
import com.github.dockerjava.zerodep.ZerodepDockerHttpClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;

@Configuration
public class DockerConfig {

        @Value("${execution.docker.host:unix:///var/run/docker.sock}")
        private String dockerHost;

        @Bean
        public DockerClient dockerClient() {
                DefaultDockerClientConfig config = DefaultDockerClientConfig.createDefaultConfigBuilder()
                                .withDockerHost(dockerHost)
                                .build();

                ZerodepDockerHttpClient httpClient = new ZerodepDockerHttpClient.Builder()
                                .dockerHost(config.getDockerHost())
                                .maxConnections(100)
                                .connectionTimeout(Duration.ofSeconds(30))
                                .responseTimeout(Duration.ofSeconds(120))
                                .build();

                return DockerClientImpl.getInstance(config, httpClient);
        }
}
