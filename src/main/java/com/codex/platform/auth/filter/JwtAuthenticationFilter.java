package com.codex.platform.auth.filter;

import com.codex.platform.auth.util.JwtUtil;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.ArrayList;

@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {

        // Extract JWT from Authorization header
        String authHeader = request.getHeader("Authorization");

        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);

            try {
                if (jwtUtil.validateToken(token)) {
                    String username = jwtUtil.extractUsername(token);

                    // Create authentication object
                    UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(
                            username,
                            null,
                            new ArrayList<>());

                    authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));

                    // Set authentication in SecurityContext
                    SecurityContextHolder.getContext().setAuthentication(authentication);
                }
            } catch (Exception e) {
                // Invalid token - continue without authentication
                logger.error("JWT validation failed: " + e.getMessage());
            }
        }

        filterChain.doFilter(request, response);
    }
}
