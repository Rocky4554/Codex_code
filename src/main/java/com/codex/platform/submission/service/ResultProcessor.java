package com.codex.platform.submission.service;

import com.codex.platform.common.enums.ProblemDifficulty;
import com.codex.platform.common.enums.SubmissionStatus;
import com.codex.platform.common.enums.UserProblemStatusEnum;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.repository.ProblemRepository;
import com.codex.platform.submission.entity.Submission;
import com.codex.platform.submission.entity.SubmissionResult;
import com.codex.platform.submission.repository.SubmissionRepository;
import com.codex.platform.submission.repository.SubmissionResultRepository;
import com.codex.platform.user.entity.User;
import com.codex.platform.user.entity.UserProblemStatus;
import com.codex.platform.user.repository.UserProblemStatusRepository;
import com.codex.platform.user.repository.UserRepository;
import com.codex.platform.user.service.LeaderboardCacheService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class ResultProcessor {

    private static final int EASY_POINTS = 10;
    private static final int MEDIUM_POINTS = 30;
    private static final int HARD_POINTS = 70;

    private final SubmissionRepository submissionRepository;
    private final SubmissionResultRepository submissionResultRepository;
    private final UserProblemStatusRepository userProblemStatusRepository;
    private final UserRepository userRepository;
    private final ProblemRepository problemRepository;
    private final LeaderboardCacheService leaderboardCacheService;

    @Transactional
    public void saveResult(Submission submission, SubmissionResult result, SubmissionStatus finalStatus) {
        try {
            SubmissionResult persistedResult = Objects.requireNonNull(result, "Submission result is required");

            // Update submission status
            submission.setStatus(finalStatus);
            submissionRepository.save(submission);

            // Save submission result
            submissionResultRepository.save(persistedResult);

            // Update user problem status if accepted
            if (finalStatus == SubmissionStatus.ACCEPTED) {
                boolean firstSolve = updateUserProblemStatus(submission);
                if (firstSolve) {
                    updateLeaderboardStats(submission);
                }
            } else {
                // Mark as attempted if not already solved
                markAsAttempted(submission);
            }

            log.info("Successfully saved result for submission: {}", submission.getId());

        } catch (Exception e) {
            log.error("Error saving result for submission: {}", submission.getId(), e);
            throw e; // Rollback transaction
        }
    }

    private boolean updateUserProblemStatus(Submission submission) {
        Optional<UserProblemStatus> existingStatus = userProblemStatusRepository
                .findByUserIdAndProblemId(submission.getUserId(), submission.getProblemId());

        if (existingStatus.isPresent()) {
            UserProblemStatus status = existingStatus.get();
            if (status.getStatus() != UserProblemStatusEnum.SOLVED) {
                status.setStatus(UserProblemStatusEnum.SOLVED);
                status.setSolvedAt(LocalDateTime.now());
                userProblemStatusRepository.save(status);
                log.info("Updated user problem status to SOLVED for user: {} problem: {}",
                        submission.getUserId(), submission.getProblemId());
                return true;
            }
            return false;
        } else {
            UserProblemStatus status = new UserProblemStatus();
            status.setUserId(submission.getUserId());
            status.setProblemId(submission.getProblemId());
            status.setStatus(UserProblemStatusEnum.SOLVED);
            status.setSolvedAt(LocalDateTime.now());
            userProblemStatusRepository.save(status);
            log.info("Created user problem status SOLVED for user: {} problem: {}",
                    submission.getUserId(), submission.getProblemId());
            return true;
        }
    }

    private void updateLeaderboardStats(Submission submission) {
        UUID userId = Objects.requireNonNull(submission.getUserId(), "Submission userId is required");
        UUID problemId = Objects.requireNonNull(submission.getProblemId(), "Submission problemId is required");

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalStateException("User not found for submission " + submission.getId()));
        Problem problem = problemRepository.findById(problemId)
                .orElseThrow(() -> new IllegalStateException("Problem not found for submission " + submission.getId()));

        ProblemDifficulty difficulty = problem.getDifficulty();
        if (difficulty == ProblemDifficulty.EASY) {
            user.setSolvedEasy(user.getSolvedEasy() + 1);
            user.setTotalScore(user.getTotalScore() + EASY_POINTS);
        } else if (difficulty == ProblemDifficulty.MEDIUM) {
            user.setSolvedMedium(user.getSolvedMedium() + 1);
            user.setTotalScore(user.getTotalScore() + MEDIUM_POINTS);
        } else if (difficulty == ProblemDifficulty.HARD) {
            user.setSolvedHard(user.getSolvedHard() + 1);
            user.setTotalScore(user.getTotalScore() + HARD_POINTS);
        } else {
            throw new IllegalStateException("Unsupported difficulty " + difficulty);
        }

        userRepository.save(user);
        leaderboardCacheService.evictLeaderboard();
        log.info("Updated leaderboard stats for user: {} after solving problem: {}",
                userId, problemId);
    }

    private void markAsAttempted(Submission submission) {
        Optional<UserProblemStatus> existingStatus = userProblemStatusRepository
                .findByUserIdAndProblemId(submission.getUserId(), submission.getProblemId());

        if (existingStatus.isEmpty()) {
            UserProblemStatus status = new UserProblemStatus();
            status.setUserId(submission.getUserId());
            status.setProblemId(submission.getProblemId());
            status.setStatus(UserProblemStatusEnum.ATTEMPTED);
            userProblemStatusRepository.save(status);
            log.info("Marked problem as ATTEMPTED for user: {} problem: {}",
                    submission.getUserId(), submission.getProblemId());
        }
    }
}
