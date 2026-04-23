package com.codex.platform.user.service;

import com.codex.platform.user.dto.LeaderboardEntryResponse;
import com.codex.platform.user.dto.CurrentUserLeaderboardResponse;
import com.codex.platform.user.entity.User;
import com.codex.platform.user.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.Pageable;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class LeaderboardServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private LeaderboardCacheService leaderboardCacheService;

    @InjectMocks
    private LeaderboardService leaderboardService;

    @Test
    void getLeaderboard_returnsRankedEntriesInRepositoryOrder() {
        User first = buildUser("raunak", 2100, 50, 30, 10, LocalDateTime.of(2024, 1, 1, 10, 0));
        User second = buildUser("amit", 1960, 60, 20, 8, LocalDateTime.of(2024, 1, 2, 10, 0));

        when(leaderboardCacheService.getLeaderboard(100)).thenReturn(Optional.empty());
        when(userRepository.findAllByOrderByTotalScoreDescSolvedHardDescCreatedAtAsc(any(Pageable.class)))
                .thenReturn(List.of(first, second));

        List<LeaderboardEntryResponse> leaderboard = leaderboardService.getLeaderboard(100);

        verify(userRepository).findAllByOrderByTotalScoreDescSolvedHardDescCreatedAtAsc(any(Pageable.class));
        verify(leaderboardCacheService).cacheLeaderboard(eq(100), any());
        assertThat(leaderboard).hasSize(2);
        assertThat(leaderboard.get(0).getRank()).isEqualTo(1);
        assertThat(leaderboard.get(0).getUsername()).isEqualTo("raunak");
        assertThat(leaderboard.get(0).getSolvedHard()).isEqualTo(10);
        assertThat(leaderboard.get(0).getTotalScore()).isEqualTo(2100);
        assertThat(leaderboard.get(1).getRank()).isEqualTo(2);
        assertThat(leaderboard.get(1).getUsername()).isEqualTo("amit");
    }

    @Test
    void getLeaderboard_capsRequestedLimitAtHundred() {
        when(leaderboardCacheService.getLeaderboard(100)).thenReturn(Optional.empty());
        when(userRepository.findAllByOrderByTotalScoreDescSolvedHardDescCreatedAtAsc(any(Pageable.class)))
                .thenReturn(List.of());

        leaderboardService.getLeaderboard(250);

        verify(userRepository).findAllByOrderByTotalScoreDescSolvedHardDescCreatedAtAsc(Pageable.ofSize(100));
    }

    @Test
    void getLeaderboard_returnsCachedEntriesWhenAvailable() {
        LeaderboardEntryResponse cachedEntry = LeaderboardEntryResponse.builder()
                .rank(1)
                .userId(UUID.randomUUID())
                .username("cached-user")
                .solvedEasy(1)
                .solvedMedium(2)
                .solvedHard(3)
                .totalScore(275)
                .build();

        when(leaderboardCacheService.getLeaderboard(50)).thenReturn(Optional.of(List.of(cachedEntry)));

        List<LeaderboardEntryResponse> leaderboard = leaderboardService.getLeaderboard(50);

        assertThat(leaderboard).containsExactly(cachedEntry);
        verify(userRepository, never()).findAllByOrderByTotalScoreDescSolvedHardDescCreatedAtAsc(any(Pageable.class));
    }

    @Test
    void getCurrentUserLeaderboardStats_returnsExactRankWithTieBreakers() {
        User currentUser = buildUser("current", 500, 10, 5, 2, LocalDateTime.of(2024, 1, 3, 10, 0));
        when(userRepository.findById(currentUser.getId())).thenReturn(Optional.of(currentUser));
        when(userRepository.countByTotalScoreGreaterThan(500)).thenReturn(3L);
        when(userRepository.countByTotalScoreAndSolvedHardGreaterThan(500, 2)).thenReturn(2L);
        when(userRepository.countByTotalScoreAndSolvedHardAndCreatedAtBefore(500, 2,
                LocalDateTime.of(2024, 1, 3, 10, 0))).thenReturn(1L);

        CurrentUserLeaderboardResponse response = leaderboardService.getCurrentUserLeaderboardStats(currentUser.getId());

        assertThat(response.getRank()).isEqualTo(7);
        assertThat(response.getUsername()).isEqualTo("current");
        assertThat(response.getSolvedEasy()).isEqualTo(10);
        assertThat(response.getSolvedMedium()).isEqualTo(5);
        assertThat(response.getSolvedHard()).isEqualTo(2);
        assertThat(response.getTotalScore()).isEqualTo(500);
    }

    private User buildUser(String username, int totalScore, int solvedEasy, int solvedMedium, int solvedHard, LocalDateTime createdAt) {
        User user = new User();
        user.setId(UUID.randomUUID());
        user.setUsername(username);
        user.setEmail(username + "@example.com");
        user.setPasswordHash("hash");
        user.setRole("USER");
        user.setCreatedAt(createdAt);
        user.setSolvedEasy(solvedEasy);
        user.setSolvedMedium(solvedMedium);
        user.setSolvedHard(solvedHard);
        user.setTotalScore(totalScore);
        return user;
    }
}
