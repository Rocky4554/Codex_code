package com.codex.platform.auth.passwordreset;

import jakarta.mail.internet.MimeMessage;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.Map;

/**
 * Sends password-reset OTP emails.
 *
 * <p>Primary path (recommended for this monorepo): HTTP webhook to the Next.js
 * Nodemailer route ({@code mail.nodemailer-webhook-url}) which uses Google SMTP.
 * Fallback: Spring {@link JavaMailSender} with the same Gmail SMTP settings.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class MailService {

    private final ObjectProvider<JavaMailSender> mailSenderProvider;

    @Value("${mail.from:${spring.mail.username:}}")
    private String fromAddress;

    @Value("${mail.nodemailer-webhook-url:}")
    private String nodemailerWebhookUrl;

    @Value("${mail.nodemailer-webhook-secret:}")
    private String nodemailerWebhookSecret;

    @Value("${spring.mail.username:}")
    private String smtpUsername;

    @Async
    public void sendPasswordResetOtp(String toEmail, String username, String otp) {
        String subject = "SprintCode password reset code";
        String html = """
                <div style="font-family:Inter,Segoe UI,sans-serif;max-width:480px;margin:0 auto;padding:24px;color:#18181b">
                  <h2 style="margin:0 0 12px;color:#10b981">SprintCode</h2>
                  <p>Hi %s,</p>
                  <p>Use this one-time code to reset your password:</p>
                  <p style="font-size:28px;letter-spacing:6px;font-weight:700;margin:20px 0">%s</p>
                  <p style="color:#71717a;font-size:14px">This code expires in 10 minutes. If you did not request a reset, you can ignore this email.</p>
                </div>
                """.formatted(escape(username), otp);

        try {
            if (nodemailerWebhookUrl != null && !nodemailerWebhookUrl.isBlank()) {
                sendViaNodemailerWebhook(toEmail, subject, html);
                log.info("Password-reset OTP email queued via Nodemailer webhook to {}", maskEmail(toEmail));
                return;
            }
            sendViaJavaMail(toEmail, subject, html);
            log.info("Password-reset OTP email sent via SMTP to {}", maskEmail(toEmail));
        } catch (Exception e) {
            // Never leak OTP / stack to clients; log for ops.
            log.error("Failed to send password-reset email to {}: {}", maskEmail(toEmail), e.getMessage());
        }
    }

    private void sendViaNodemailerWebhook(String to, String subject, String html) {
        RestClient.create()
                .post()
                .uri(nodemailerWebhookUrl)
                .contentType(MediaType.APPLICATION_JSON)
                .header("X-Mail-Secret", nodemailerWebhookSecret == null ? "" : nodemailerWebhookSecret)
                .body(Map.of(
                        "to", to,
                        "subject", subject,
                        "html", html,
                        "from", fromAddress == null || fromAddress.isBlank() ? smtpUsername : fromAddress))
                .retrieve()
                .toBodilessEntity();
    }

    private void sendViaJavaMail(String to, String subject, String html) throws Exception {
        JavaMailSender mailSender = mailSenderProvider.getIfAvailable();
        if (mailSender == null || smtpUsername == null || smtpUsername.isBlank()) {
            throw new IllegalStateException(
                    "No mail transport configured. Set mail.nodemailer-webhook-url or spring.mail.*");
        }
        MimeMessage message = mailSender.createMimeMessage();
        MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
        helper.setTo(to);
        helper.setFrom(fromAddress == null || fromAddress.isBlank() ? smtpUsername : fromAddress);
        helper.setSubject(subject);
        helper.setText(html, true);
        mailSender.send(message);
    }

    private static String maskEmail(String email) {
        if (email == null || !email.contains("@")) return "***";
        int at = email.indexOf('@');
        String local = email.substring(0, at);
        String domain = email.substring(at);
        String maskedLocal = local.length() <= 2 ? "**" : local.charAt(0) + "***" + local.charAt(local.length() - 1);
        return maskedLocal + domain;
    }

    private static String escape(String s) {
        if (s == null) return "";
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;");
    }
}
