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
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ResultProcessorTest {

    @Mock
    private SubmissionRepository submissionRepository;

    @Mock
    private SubmissionResultRepository submissionResultRepository;

    @Mock
    private UserProblemStatusRepository userProblemStatusRepository;

    @Mock
    private UserRepository userRepository;

    @Mock
    private ProblemRepository problemRepository;

    @Mock
    private LeaderboardCacheService leaderboardCacheService;

    @InjectMocks
    private ResultProcessor resultProcessor;

    @ParameterizedTest
    @CsvSource({
            "EASY,10,1,0,0",
            "MEDIUM,30,0,1,0",
            "HARD,70,0,0,1"
    })
    void saveResult_firstAcceptedSolve_updatesSolvedStatusAndScore(
            ProblemDifficulty difficulty,
            int expectedScore,
            int expectedEasy,
            int expectedMedium,
            int expectedHard) {
        Submission submission = buildSubmission();
        SubmissionResult result = new SubmissionResult();
        User user = buildUser(submission.getUserId());
        Problem problem = buildProblem(submission.getProblemId(), difficulty);

        when(userProblemStatusRepository.findByUserIdAndProblemId(submission.getUserId(), submission.getProblemId()))
                .thenReturn(Optional.empty());
        when(userRepository.findById(submission.getUserId())).thenReturn(Optional.of(user));
        when(problemRepository.findById(submission.getProblemId())).thenReturn(Optional.of(problem));
        when(submissionRepository.save(any(Submission.class))).thenAnswer(invocation -> invocation.getArgument(0));
        when(submissionResultRepository.save(any(SubmissionResult.class))).thenAnswer(invocation -> invocation.getArgument(0));
        when(userProblemStatusRepository.save(any(UserProblemStatus.class))).thenAnswer(invocation -> invocation.getArgument(0));
        when(userRepository.save(any(User.class))).thenAnswer(invocation -> invocation.getArgument(0));

        resultProcessor.saveResult(submission, result, SubmissionStatus.ACCEPTED);

        ArgumentCaptor<UserProblemStatus> statusCaptor = ArgumentCaptor.forClass(UserProblemStatus.class);
        verify(userProblemStatusRepository).save(statusCaptor.capture());
        UserProblemStatus savedStatus = statusCaptor.getValue();
        assertThat(savedStatus.getStatus()).isEqualTo(UserProblemStatusEnum.SOLVED);
        assertThat(savedStatus.getSolvedAt()).isNotNull();

        ArgumentCaptor<User> userCaptor = ArgumentCaptor.forClass(User.class);
        verify(userRepository).save(userCaptor.capture());
        User savedUser = userCaptor.getValue();
        assertThat(savedUser.getSolvedEasy()).isEqualTo(expectedEasy);
        assertThat(savedUser.getSolvedMedium()).isEqualTo(expectedMedium);
        assertThat(savedUser.getSolvedHard()).isEqualTo(expectedHard);
        assertThat(savedUser.getTotalScore()).isEqualTo(expectedScore);
        verify(leaderboardCacheService).evictLeaderboard();
    }

    @Test
    void saveResult_repeatAcceptedSolve_doesNotIncrementScore() {
        Submission submission = buildSubmission();
        SubmissionResult result = new SubmissionResult();
        UserProblemStatus existingStatus = new UserProblemStatus(
                submission.getUserId(),
                submission.getProblemId(),
                UserProblemStatusEnum.SOLVED,
                null
        );

        when(userProblemStatusRepository.findByUserIdAndProblemId(submission.getUserId(), submission.getProblemId()))
                .thenReturn(Optional.of(existingStatus));
        when(submissionRepository.save(any(Submission.class))).thenAnswer(invocation -> invocation.getArgument(0));
        when(submissionResultRepository.save(any(SubmissionResult.class))).thenAnswer(invocation -> invocation.getArgument(0));

        resultProcessor.saveResult(submission, result, SubmissionStatus.ACCEPTED);

        verify(problemRepository, never()).findById(any());
        verify(userRepository, never()).findById(any());
        verify(userRepository, never()).save(any());
        verify(leaderboardCacheService, never()).evictLeaderboard();
    }

    @Test
    void saveResult_wrongAnswer_marksAttemptedWithoutUpdatingScore() {
        Submission submission = buildSubmission();
        SubmissionResult result = new SubmissionResult();

        when(userProblemStatusRepository.findByUserIdAndProblemId(submission.getUserId(), submission.getProblemId()))
                .thenReturn(Optional.empty());
        when(submissionRepository.save(any(Submission.class))).thenAnswer(invocation -> invocation.getArgument(0));
        when(submissionResultRepository.save(any(SubmissionResult.class))).thenAnswer(invocation -> invocation.getArgument(0));
        when(userProblemStatusRepository.save(any(UserProblemStatus.class))).thenAnswer(invocation -> invocation.getArgument(0));

        resultProcessor.saveResult(submission, result, SubmissionStatus.WRONG_ANSWER);

        ArgumentCaptor<UserProblemStatus> statusCaptor = ArgumentCaptor.forClass(UserProblemStatus.class);
        verify(userProblemStatusRepository).save(statusCaptor.capture());
        assertThat(statusCaptor.getValue().getStatus()).isEqualTo(UserProblemStatusEnum.ATTEMPTED);
        verify(problemRepository, never()).findById(any());
        verify(userRepository, never()).save(any());
        verify(leaderboardCacheService, never()).evictLeaderboard();
    }

    private Submission buildSubmission() {
        Submission submission = new Submission();
        submission.setId(UUID.randomUUID());
        submission.setUserId(UUID.randomUUID());
        submission.setProblemId(UUID.randomUUID());
        submission.setLanguageId(UUID.randomUUID());
        submission.setSourceCode("print('hi')");
        return submission;
    }

    private User buildUser(UUID userId) {
        User user = new User();
        user.setId(userId);
        user.setUsername("raunak");
        user.setEmail("raunak@example.com");
        user.setPasswordHash("hash");
        user.setRole("USER");
        user.setSolvedEasy(0);
        user.setSolvedMedium(0);
        user.setSolvedHard(0);
        user.setTotalScore(0);
        return user;
    }

    private Problem buildProblem(UUID problemId, ProblemDifficulty difficulty) {
        Problem problem = new Problem();
        problem.setId(problemId);
        problem.setTitle("Two Sum");
        problem.setDifficulty(difficulty);
        problem.setTimeLimitMs(1000);
        problem.setMemoryLimitMb(256);
        return problem;
    }
}
