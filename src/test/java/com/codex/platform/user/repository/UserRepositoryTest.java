package com.codex.platform.user.repository;

import com.codex.platform.user.entity.User;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;

import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
@ActiveProfiles("test")
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.ANY)
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Test
    void findAllByOrderByTotalScoreDescSolvedHardDescCreatedAtAsc_sortsByScoreThenHardThenCreatedAt() {
        User earlierJoiner = saveUser("earlier", 500, 2, LocalDateTime.of(2024, 1, 1, 9, 0));
        User harderSolver = saveUser("harder", 500, 3, LocalDateTime.of(2024, 1, 2, 9, 0));
        User topScore = saveUser("top", 600, 1, LocalDateTime.of(2024, 1, 3, 9, 0));

        List<User> users = userRepository.findAllByOrderByTotalScoreDescSolvedHardDescCreatedAtAsc(
                org.springframework.data.domain.Pageable.ofSize(10)
        );

        assertThat(users)
                .extracting(User::getUsername)
                .containsExactly("top", "harder", "earlier");
    }

    private User saveUser(String username, int totalScore, int solvedHard, LocalDateTime createdAt) {
        User user = new User();
        user.setUsername(username);
        user.setEmail(username + "@example.com");
        user.setPasswordHash("hash");
        user.setRole("USER");
        user.setSolvedEasy(0);
        user.setSolvedMedium(0);
        user.setSolvedHard(solvedHard);
        user.setTotalScore(totalScore);
        User saved = userRepository.saveAndFlush(user);
        jdbcTemplate.update(
                "update users set created_at = ? where id = ?",
                Timestamp.valueOf(createdAt),
                saved.getId()
        );
        return userRepository.findById(saved.getId()).orElseThrow();
    }
}
