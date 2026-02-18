package com.codex.platform.config;

import org.redisson.Redisson;
import org.redisson.api.RedissonClient;
import org.redisson.config.Config;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;

@Configuration
public class RedissonConfig {

    @Value("${redisson.single-server-config.address}")
    private String address;

    @Value("${redisson.single-server-config.username:default}")
    private String username;

    @Value("${redisson.single-server-config.password}")
    private String password;

    @Value("${redisson.single-server-config.connection-pool-size:64}")
    private int connectionPoolSize;

    @Value("${redisson.single-server-config.connection-minimum-idle-size:10}")
    private int connectionMinimumIdleSize;

    @Bean(destroyMethod = "shutdown")
    @Primary
    public RedissonClient redissonClient() {
        Config config = new Config();
        config.useSingleServer()
                .setAddress(address)
                .setUsername(username)
                .setPassword(password)
                .setConnectionPoolSize(connectionPoolSize)
                .setConnectionMinimumIdleSize(connectionMinimumIdleSize);

        return Redisson.create(config);
    }
}
