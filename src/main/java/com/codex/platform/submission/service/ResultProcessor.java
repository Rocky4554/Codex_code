package com.codex.platform.submission.service;

import com.codex.platform.common.enums.SubmissionStatus;
import com.codex.platform.common.enums.UserProblemStatusEnum;
import com.codex.platform.submission.entity.Submission;
import com.codex.platform.submission.entity.SubmissionResult;
import com.codex.platform.submission.repository.SubmissionRepository;
import com.codex.platform.submission.repository.SubmissionResultRepository;
import com.codex.platform.user.entity.UserProblemStatus;
import com.codex.platform.user.repository.UserProblemStatusRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class ResultProcessor {

    private final SubmissionRepository submissionRepository;
    private final SubmissionResultRepository submissionResultRepository;
    private final UserProblemStatusRepository userProblemStatusRepository;

    @Transactional
    public void saveResult(Submission submission, SubmissionResult result, SubmissionStatus finalStatus) {
        try {
            // Update submission status
            submission.setStatus(finalStatus);
            submissionRepository.save(submission);

            // Save submission result
            submissionResultRepository.save(result);

            // Update user problem status if accepted
            if (finalStatus == SubmissionStatus.ACCEPTED) {
                updateUserProblemStatus(submission);
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

    private void updateUserProblemStatus(Submission submission) {
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
            }
        } else {
            UserProblemStatus status = new UserProblemStatus();
            status.setUserId(submission.getUserId());
            status.setProblemId(submission.getProblemId());
            status.setStatus(UserProblemStatusEnum.SOLVED);
            status.setSolvedAt(LocalDateTime.now());
            userProblemStatusRepository.save(status);
            log.info("Created user problem status SOLVED for user: {} problem: {}",
                    submission.getUserId(), submission.getProblemId());
        }
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
