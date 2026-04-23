package com.codex.platform.user.service;

import com.codex.platform.common.enums.ProblemDifficulty;
import com.codex.platform.common.enums.UserProblemStatusEnum;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.repository.ProblemRepository;
import com.codex.platform.user.entity.User;
import com.codex.platform.user.entity.UserProblemStatus;
import com.codex.platform.user.repository.UserProblemStatusRepository;
import com.codex.platform.user.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class LeaderboardStatsBackfillServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private UserProblemStatusRepository userProblemStatusRepository;

    @Mock
    private ProblemRepository problemRepository;

    @Mock
    private LeaderboardCacheService leaderboardCacheService;

    @InjectMocks
    private LeaderboardStatsBackfillService leaderboardStatsBackfillService;

    @Test
    void backfillStats_recomputesUserTotalsFromSolvedProblems() {
        UUID easyProblemId = UUID.randomUUID();
        UUID hardProblemId = UUID.randomUUID();
        User user = buildUser(UUID.randomUUID(), 0, 0, 0, 0);

        when(userRepository.findAll()).thenReturn(List.of(user));
        when(userProblemStatusRepository.findByUserId(user.getId())).thenReturn(List.of(
                new UserProblemStatus(user.getId(), easyProblemId, UserProblemStatusEnum.SOLVED, null),
                new UserProblemStatus(user.getId(), UUID.randomUUID(), UserProblemStatusEnum.ATTEMPTED, null),
                new UserProblemStatus(user.getId(), hardProblemId, UserProblemStatusEnum.SOLVED, null)
        ));
        when(problemRepository.findAllById(List.of(easyProblemId, hardProblemId))).thenReturn(List.of(
                buildProblem(easyProblemId, ProblemDifficulty.EASY),
                buildProblem(hardProblemId, ProblemDifficulty.HARD)
        ));

        leaderboardStatsBackfillService.backfillStats();

        ArgumentCaptor<User> userCaptor = ArgumentCaptor.forClass(User.class);
        verify(userRepository).save(userCaptor.capture());
        User updatedUser = userCaptor.getValue();
        assertThat(updatedUser.getSolvedEasy()).isEqualTo(1);
        assertThat(updatedUser.getSolvedMedium()).isEqualTo(0);
        assertThat(updatedUser.getSolvedHard()).isEqualTo(1);
        assertThat(updatedUser.getTotalScore()).isEqualTo(80);
        verify(leaderboardCacheService).evictLeaderboard();
    }

    @Test
    void backfillStats_skipsUsersWhoseStoredStatsAlreadyMatch() {
        UUID easyProblemId = UUID.randomUUID();
        User user = buildUser(UUID.randomUUID(), 10, 1, 0, 0);

        when(userRepository.findAll()).thenReturn(List.of(user));
        when(userProblemStatusRepository.findByUserId(user.getId())).thenReturn(List.of(
                new UserProblemStatus(user.getId(), easyProblemId, UserProblemStatusEnum.SOLVED, null)
        ));
        when(problemRepository.findAllById(List.of(easyProblemId))).thenReturn(List.of(
                buildProblem(easyProblemId, ProblemDifficulty.EASY)
        ));

        leaderboardStatsBackfillService.backfillStats();

        verify(userRepository, never()).save(user);
        verify(leaderboardCacheService, never()).evictLeaderboard();
    }

    private User buildUser(UUID userId, int totalScore, int solvedEasy, int solvedMedium, int solvedHard) {
        User user = new User();
        user.setId(userId);
        user.setUsername("user-" + userId);
        user.setEmail(userId + "@example.com");
        user.setPasswordHash("hash");
        user.setRole("USER");
        user.setSolvedEasy(solvedEasy);
        user.setSolvedMedium(solvedMedium);
        user.setSolvedHard(solvedHard);
        user.setTotalScore(totalScore);
        return user;
    }

    private Problem buildProblem(UUID problemId, ProblemDifficulty difficulty) {
        Problem problem = new Problem();
        problem.setId(problemId);
        problem.setTitle("Problem");
        problem.setDifficulty(difficulty);
        problem.setTimeLimitMs(1000);
        problem.setMemoryLimitMb(256);
        return problem;
    }
}
