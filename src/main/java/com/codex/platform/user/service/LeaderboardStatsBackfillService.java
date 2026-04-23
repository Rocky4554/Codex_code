package com.codex.platform.user.service;

import com.codex.platform.common.enums.ProblemDifficulty;
import com.codex.platform.common.enums.UserProblemStatusEnum;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.repository.ProblemRepository;
import com.codex.platform.user.entity.User;
import com.codex.platform.user.entity.UserProblemStatus;
import com.codex.platform.user.repository.UserProblemStatusRepository;
import com.codex.platform.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class LeaderboardStatsBackfillService {

    private final UserRepository userRepository;
    private final UserProblemStatusRepository userProblemStatusRepository;
    private final ProblemRepository problemRepository;
    private final LeaderboardCacheService leaderboardCacheService;

    public void backfillStats() {
        List<User> users = userRepository.findAll();
        int updatedUsers = 0;

        for (User user : users) {
            List<UUID> solvedProblemIds = userProblemStatusRepository.findByUserId(user.getId()).stream()
                    .filter(status -> status.getStatus() == UserProblemStatusEnum.SOLVED)
                    .map(UserProblemStatus::getProblemId)
                    .toList();

            List<Problem> solvedProblems = problemRepository.findAllById(new ArrayList<>(solvedProblemIds));

            int solvedEasy = 0;
            int solvedMedium = 0;
            int solvedHard = 0;

            for (Problem problem : solvedProblems) {
                if (problem.getDifficulty() == ProblemDifficulty.EASY) {
                    solvedEasy++;
                } else if (problem.getDifficulty() == ProblemDifficulty.MEDIUM) {
                    solvedMedium++;
                } else if (problem.getDifficulty() == ProblemDifficulty.HARD) {
                    solvedHard++;
                }
            }

            int totalScore = (solvedEasy * 10) + (solvedMedium * 30) + (solvedHard * 70);
            if (statsChanged(user, solvedEasy, solvedMedium, solvedHard, totalScore)) {
                user.setSolvedEasy(solvedEasy);
                user.setSolvedMedium(solvedMedium);
                user.setSolvedHard(solvedHard);
                user.setTotalScore(totalScore);
                userRepository.save(user);
                updatedUsers++;
            }
        }

        if (updatedUsers > 0) {
            leaderboardCacheService.evictLeaderboard();
        }
        log.info("Leaderboard stats backfill complete. Updated {} users.", updatedUsers);
    }

    private boolean statsChanged(User user, int solvedEasy, int solvedMedium, int solvedHard, int totalScore) {
        return user.getSolvedEasy() != solvedEasy
                || user.getSolvedMedium() != solvedMedium
                || user.getSolvedHard() != solvedHard
                || user.getTotalScore() != totalScore;
    }
}
