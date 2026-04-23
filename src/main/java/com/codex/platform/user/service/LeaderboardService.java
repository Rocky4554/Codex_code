package com.codex.platform.user.service;

import com.codex.platform.user.dto.LeaderboardEntryResponse;
import com.codex.platform.user.dto.CurrentUserLeaderboardResponse;
import com.codex.platform.user.entity.User;
import com.codex.platform.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Objects;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class LeaderboardService {

    private static final int DEFAULT_LIMIT = 100;
    private static final int MAX_LIMIT = 100;

    private final UserRepository userRepository;
    private final LeaderboardCacheService leaderboardCacheService;

    public List<LeaderboardEntryResponse> getLeaderboard(int requestedLimit) {
        int limit = requestedLimit <= 0 ? DEFAULT_LIMIT : Math.min(requestedLimit, MAX_LIMIT);
        java.util.Optional<List<LeaderboardEntryResponse>> cachedLeaderboard = leaderboardCacheService.getLeaderboard(limit);
        if (cachedLeaderboard.isPresent()) {
            return cachedLeaderboard.get();
        }

        List<User> users = userRepository.findAllByOrderByTotalScoreDescSolvedHardDescCreatedAtAsc(
                PageRequest.of(0, limit)
        );

        List<LeaderboardEntryResponse> leaderboard = java.util.stream.IntStream.range(0, users.size())
                .mapToObj(index -> mapUser(users.get(index), index + 1))
                .toList();
        leaderboardCacheService.cacheLeaderboard(limit, leaderboard);
        return leaderboard;
    }

    public CurrentUserLeaderboardResponse getCurrentUserLeaderboardStats(UUID userId) {
        UUID requiredUserId = Objects.requireNonNull(userId, "User id is required");
        User user = userRepository.findById(requiredUserId)
                .orElseThrow(() -> new IllegalStateException("User not found: " + userId));

        long higherScores = userRepository.countByTotalScoreGreaterThan(user.getTotalScore());
        long sameScoreMoreHard = userRepository.countByTotalScoreAndSolvedHardGreaterThan(
                user.getTotalScore(),
                user.getSolvedHard()
        );
        long sameScoreSameHardEarlierCreated = userRepository.countByTotalScoreAndSolvedHardAndCreatedAtBefore(
                user.getTotalScore(),
                user.getSolvedHard(),
                user.getCreatedAt()
        );
        int rank = (int) (higherScores + sameScoreMoreHard + sameScoreSameHardEarlierCreated + 1);

        return CurrentUserLeaderboardResponse.builder()
                .rank(rank)
                .userId(user.getId())
                .username(user.getUsername())
                .solvedEasy(user.getSolvedEasy())
                .solvedMedium(user.getSolvedMedium())
                .solvedHard(user.getSolvedHard())
                .totalScore(user.getTotalScore())
                .build();
    }

    private LeaderboardEntryResponse mapUser(User user, int rank) {
        return LeaderboardEntryResponse.builder()
                .rank(rank)
                .userId(user.getId())
                .username(user.getUsername())
                .solvedEasy(user.getSolvedEasy())
                .solvedMedium(user.getSolvedMedium())
                .solvedHard(user.getSolvedHard())
                .totalScore(user.getTotalScore())
                .build();
    }
}
