package com.codex.platform.user.service;

import com.codex.platform.user.dto.LeaderboardEntryResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.redisson.api.RBucket;
import org.redisson.api.RKeys;
import org.redisson.api.RedissonClient;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class LeaderboardCacheServiceTest {

    @Mock
    private RedissonClient redissonClient;

    @Mock
    private RBucket<Object> bucket;

    @Mock
    private RKeys keys;

    private LeaderboardCacheService leaderboardCacheService;

    @BeforeEach
    void setUp() {
        leaderboardCacheService = new LeaderboardCacheService(redissonClient, new ObjectMapper());
    }

    @Test
    void getLeaderboard_deserializesCachedJson() throws Exception {
        List<LeaderboardEntryResponse> entries = List.of(
                LeaderboardEntryResponse.builder()
                        .rank(1)
                        .userId(UUID.randomUUID())
                        .username("raunak")
                        .solvedEasy(10)
                        .solvedMedium(5)
                        .solvedHard(2)
                        .totalScore(390)
                        .build()
        );
        String payload = new ObjectMapper().writeValueAsString(entries);

        when(redissonClient.getBucket("leaderboard:top:100")).thenReturn(bucket);
        when(bucket.get()).thenReturn(payload);

        Optional<List<LeaderboardEntryResponse>> cached = leaderboardCacheService.getLeaderboard(100);

        assertThat(cached).isPresent();
        assertThat(cached.orElseThrow()).hasSize(1);
        assertThat(cached.orElseThrow().get(0).getUsername()).isEqualTo("raunak");
    }

    @Test
    void evictLeaderboard_deletesAllLeaderboardKeys() {
        when(redissonClient.getKeys()).thenReturn(keys);

        leaderboardCacheService.evictLeaderboard();

        verify(keys).deleteByPattern("leaderboard:top:*");
    }
}
