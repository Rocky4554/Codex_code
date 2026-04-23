package com.codex.platform.problem.dto;

import com.codex.platform.common.enums.ProblemDifficulty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProblemDetailResponse {

    private UUID id;
    private String title;
    private String description;
    private ProblemDifficulty difficulty;
    private Integer timeLimitMs;
    private Integer memoryLimitMb;
    private Integer orderNum;
    private List<ExampleDto> examples;
    private List<TestCaseDto> testCases;
    private List<String> constraints;
    private List<String> topics;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ExampleDto {
        private UUID id;
        private String input;
        private String output;
        private String explanation;
        private Integer displayOrder;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TestCaseDto {
        private UUID id;
        private String input;
        private String expectedOutput;
        private Boolean isSample;
    }
}
