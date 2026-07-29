require("dotenv").config();
const express = require("express");
const cors = require("cors");
const nodemailer = require("nodemailer");
const path = require("path");

const app = express();
app.use(
  cors({
    origin: ["http://localhost:5173", "http://127.0.0.1:5173"],
    methods: ["GET", "POST"],
  }),
);
app.use(express.json({ limit: "100mb" }));
app.use(express.urlencoded({ limit: "100mb", extended: true }));

// ── Nodemailer transporter (Office365) ───────────────────────────────────────
const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: parseInt(process.env.SMTP_PORT),
  secure: false, // false for 587 (STARTTLS)
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
  tls: {
    ciphers: "SSLv3",
    rejectUnauthorized: false,
  },
});

// Shared logo attachment — reused across every email that references cid:invengerlogo
const logoAttachment = {
  filename: "invenger-logo.png",
  path: path.join(__dirname, "assets", "invenger-logo.png"),
  cid: "invengerlogo",
};

const { generateEmployeeLetter } = require("./generate-letter");
app.post("/generate-letter", async (req, res) => {
  try {
    const buffer = await generateEmployeeLetter(req.body);
    res.set({
      "Content-Type":
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "Content-Disposition": `attachment; filename="${req.body.first_name}_${req.body.last_name}_Details.docx"`,
    });
    res.send(buffer);
  } catch (err) {
    console.error("[LETTER] Generation failed:", err.message);
    res.status(500).json({ error: err.message });
  }
});

// ── Employee Letter Email Template ──────────────────────────────────────────
function employeeLetterEmailTemplate({ employee_name }) {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }
    .container { max-width: 600px; margin: 40px auto; background: #ffffff;
                 border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    .top-strip { background: #1d4ed8; height: 6px; }
    .body { padding: 32px 40px; }
    .body p { color: #374151; font-size: 15px; line-height: 1.7; margin: 0 0 16px; }
    .info-box { background: #eff6ff; border: 1px solid #bfdbfe;
                border-radius: 8px; padding: 14px 18px; margin: 18px 0;
                font-size: 13px; color: #1e40af; }
    .sign-logo { height: 18px; margin-top: 10px; }
    .footer { background: #f8fafc; padding: 20px 40px; text-align: center;
              color: #9ca3af; font-size: 12px; border-top: 1px solid #e5e7eb; }
  </style>
</head>
<body>
  <div class="container">
    <div class="top-strip"></div>
    <div class="body">
      <p style="font-size:18px; font-weight:700; color:#1e293b; margin:0 0 18px;">Employee Details</p>
      <p>Dear <strong>${employee_name}</strong>,</p>
      <p>Greetings from Invenger Technologies.</p>
      <p>Please find attached your <strong>Employee Details Document</strong>,
         which includes your personal, professional, and compensation information
         on record with us.</p>
      <div class="info-box">
        📎 Attachment: ${employee_name.replace(/\s+/g, "_")}_Details.docx
      </div>
      <p>Kindly review the attached document and reach out to HR if you notice
         any discrepancy or have questions regarding the details mentioned.</p>
      <p>Warm regards,<br><strong>Invenger HR Team</strong></p>
      <img src="cid:invengerlogo" alt="Invenger" width="70" height="18" style="height:18px; width:70px; margin-top:10px; display:block;" />
    </div>
    <div class="footer">
      <p>Invenger Technologies &nbsp;·&nbsp; Confidential HR Communication</p>
      <p>© ${new Date().getFullYear()} Invenger Technologies Pvt. Ltd.</p>
    </div>
  </div>
</body>
</html>`;
}

app.post("/send-employee-letter", async (req, res) => {
  try {
    const { employee_email, employee_name, ...letterData } = req.body;

    if (!employee_email) {
      return res.status(400).json({ error: "employee_email is required" });
    }

    const buffer = await generateEmployeeLetter(letterData);

    await transporter.sendMail({
      from: `"${process.env.FROM_NAME}" <${process.env.SMTP_USER}>`,
      to: employee_email,
      subject: `Your Employee Details — Invenger`,
      html: employeeLetterEmailTemplate({ employee_name }),
      attachments: [
        {
          filename: `${letterData.first_name}_${letterData.last_name}_Details.docx`,
          content: buffer,
        },
        logoAttachment,
      ],
    });

    console.log(`[LETTER] Document emailed to ${employee_email}`);
    res.json({ success: true });
  } catch (err) {
    console.error("[LETTER] Send failed:", err.message);
    res.status(500).json({ error: err.message });
  }
});

// ── Email Templates ───────────────────────────────────────────────────────────
function concernTemplate({ employee_name, category, message, response_link }) {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }
    .container { max-width: 600px; margin: 40px auto; background: #ffffff;
                 border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    .body { padding: 32px 40px; }
    .body p { color: #374151; font-size: 15px; line-height: 1.6; margin: 0 0 16px; }
    .category-badge { display: inline-block; background: #eff6ff; color: #1d4ed8;
                      border: 1px solid #bfdbfe; border-radius: 8px;
                      padding: 4px 12px; font-size: 13px; font-weight: 600;
                      text-transform: capitalize; margin-bottom: 16px; }
    .message-box { background: #f8fafc; border-left: 4px solid #2563eb;
                   border-radius: 0 8px 8px 0; padding: 16px 20px;
                   color: #374151; font-size: 14px; line-height: 1.6;
                   margin: 16px 0; }
    .btn { display: inline-block; background: #2563eb; color: #ffffff !important;
           text-decoration: none; padding: 12px 28px; border-radius: 8px;
           font-weight: 700; font-size: 14px; margin: 20px 0; }
    .sign-logo { height: 18px; margin-top: 10px; }
    .footer { background: #f8fafc; padding: 20px 40px; text-align: center;
              color: #9ca3af; font-size: 12px; border-top: 1px solid #e5e7eb; }
  </style>
</head>
<body>
  <div class="container">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#1d4ed8">
      <tr>
        <td align="center" style="padding:32px 40px; background-color:#1d4ed8;">
          <p style="color:#ffffff; margin:0; font-size:20px; font-weight:700; font-family:Arial, sans-serif;">Employee Feedback Survey</p>
        </td>
      </tr>
    </table>
    <div class="body">
      <p>Dear <strong>${employee_name}</strong>,</p>
      <p>HR has raised a feedback request regarding the following concern:</p>
      <span class="category-badge">${category}</span>
      <div class="message-box">${message}</div>
      <p>Please click the button below to submit your private response.
         Your response is <strong>confidential</strong> and only visible to HR.</p>
      <a href="${response_link}" class="btn">Submit Your Response</a>
      <p style="font-size:13px; color:#6b7280;">
        Or copy this link: <br>
        <span style="color:#2563eb;">${response_link}</span>
      </p>
      <p>Warm regards,<br><strong>Invenger HR Team</strong></p>
      <img src="cid:invengerlogo" alt="Invenger" width="70" height="18" style="height:18px; width:70px; margin-top:10px; display:block;" />
    </div>
    <div class="footer">
      <p>Invenger Technologies &nbsp;·&nbsp; This is a confidential HR communication.</p>
      <p>Please do not forward this email.</p>
    </div>
  </div>
</body>
</html>`;
}

function exitInterviewTemplate({ employee_name, form_link }) {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }
    .container { max-width: 600px; margin: 40px auto; background: #ffffff;
                 border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    .body { padding: 32px 40px; }
    .body p { color: #374151; font-size: 15px; line-height: 1.6; margin: 0 0 16px; }
    .info-box { background: #eff6ff; border: 1px solid #bfdbfe;
                border-radius: 8px; padding: 16px 20px; margin: 16px 0; }
    .info-box p { margin: 4px 0; font-size: 14px; color: #1e40af; }
    .btn { display: inline-block; background: #2563eb; color: #ffffff !important;
           text-decoration: none; padding: 12px 28px; border-radius: 8px;
           font-weight: 700; font-size: 14px; margin: 20px 0; }
    .sign-logo { height: 18px; margin-top: 10px; }
    .footer { background: #f8fafc; padding: 20px 40px; text-align: center;
              color: #9ca3af; font-size: 12px; border-top: 1px solid #e5e7eb; }
  </style>
</head>
<body>
  <div class="container">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#1d4ed8">
      <tr>
        <td align="center" style="padding:32px 40px; background-color:#1d4ed8;">
          <p style="color:#ffffff; margin:0; font-size:22px; font-weight:700; font-family:Arial, sans-serif;">Exit Interview</p>
          <p style="color:#bfdbfe; margin:8px 0 0; font-size:13px; font-family:Arial, sans-serif;">Confidential · INV/HR/EIQ/v1.0</p>
        </td>
      </tr>
    </table>
    <div class="body">
      <p>Dear <strong>${employee_name}</strong>,</p>
      <p>As part of the employee separation process at <strong>Invenger Technologies</strong>,
         we request you to complete the Exit Interview Questionnaire.</p>
      <p>Your feedback is extremely valuable and helps us improve our workplace,
         policies, and employee experience. All responses will remain
         <strong>strictly confidential</strong> and will be reviewed only by the HR team.</p>
      <div class="info-box">
        <p>📋 <strong>Takes about:</strong> 10–15 minutes</p>
        <p>🔒 <strong>Privacy:</strong> Responses visible to HR only</p>
        <p>✏️  <strong>Editable:</strong> No — submit once only</p>
      </div>
      <p>Click the button below to begin:</p>
      <a href="${form_link}" class="btn">Start Exit Interview</a>
      <p style="font-size:13px; color:#6b7280;">
        Or copy this link: <br>
        <span style="color:#2563eb;">${form_link}</span>
      </p>
      <p>Thank you for your time and contribution to Invenger.
         We wish you all the best in your future endeavours.</p>
      <p>Warm regards,<br><strong>Invenger HR Team</strong></p>
      <img src="cid:invengerlogo" alt="Invenger" width="70" height="18" style="height:18px; width:70px; margin-top:10px; display:block;" />
    </div>
    <div class="footer">
      <p>Invenger Technologies &nbsp;·&nbsp; Confidential HR Communication</p>
      <p>Doc: INV/HR/EIQ/v1.0</p>
    </div>
  </div>
</body>
</html>`;
}

// ── Routes ────────────────────────────────────────────────────────────────────

// Health check
app.get("/", (req, res) => {
  res.json({ status: "ok", service: "Invenger Email Webhook" });
});

// Send concern/feedback request email
app.post("/send-concern", async (req, res) => {
  const { employee_name, employee_email, category, message, response_link } =
    req.body;

  if (!employee_email) {
    return res.status(400).json({ error: "employee_email is required" });
  }

  try {
    await transporter.sendMail({
      from: `"${process.env.FROM_NAME}" <${process.env.SMTP_USER}>`,
      to: employee_email,
      subject: `Employee Feedback Survey — ${category} | Invenger`,
      html: concernTemplate({ employee_name, category, message, response_link }),
      attachments: [logoAttachment],
    });

    console.log(`[CONCERN] Email sent to ${employee_email}`);
    res.json({ success: true, message: `Email sent to ${employee_email}` });
  } catch (err) {
    console.error("[CONCERN] Email failed:", err.message);
    res.status(500).json({ error: err.message });
  }
});

// Send exit interview email
app.post("/send-exit-interview", async (req, res) => {
  const { employee_name, employee_email, form_link } = req.body;

  if (!employee_email) {
    return res.status(400).json({ error: "employee_email is required" });
  }

  try {
    await transporter.sendMail({
      from: `"${process.env.FROM_NAME}" <${process.env.SMTP_USER}>`,
      to: employee_email,
      subject: "Your Exit Interview — Invenger",
      html: exitInterviewTemplate({ employee_name, form_link }),
      attachments: [logoAttachment],
    });

    console.log(`[EXIT INTERVIEW] Email sent to ${employee_email}`);
    res.json({ success: true, message: `Email sent to ${employee_email}` });
  } catch (err) {
    console.error("[EXIT INTERVIEW] Email failed:", err.message);
    res.status(500).json({ error: err.message });
  }
});

// ── Reminder Email Templates ───────────────────────────────────────────────
function exitInterviewReminderTemplate({ employee_name, form_link }) {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }
    .container { max-width: 600px; margin: 40px auto; background: #ffffff;
                 border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    .body { padding: 32px 40px; }
    .body p { color: #374151; font-size: 15px; line-height: 1.6; margin: 0 0 16px; }
    .reminder-box { background: #fffbeb; border: 1px solid #fde68a;
                border-radius: 8px; padding: 16px 20px; margin: 16px 0; }
    .reminder-box p { margin: 0; font-size: 14px; color: #92400e; font-weight: 600; }
    .btn { display: inline-block; background: #d97706; color: #ffffff !important;
           text-decoration: none; padding: 12px 28px; border-radius: 8px;
           font-weight: 700; font-size: 14px; margin: 20px 0; }
    .sign-logo { height: 18px; margin-top: 10px; }
    .footer { background: #f8fafc; padding: 20px 40px; text-align: center;
              color: #9ca3af; font-size: 12px; border-top: 1px solid #e5e7eb; }
  </style>
</head>
<body>
  <div class="container">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#d97706">
      <tr>
        <td align="center" style="padding:32px 40px; background-color:#d97706;">
          <p style="color:#ffffff; margin:0; font-size:20px; font-weight:700; font-family:Arial, sans-serif;">Reminder — Exit Interview Pending</p>
          <p style="color:#fde68a; margin:8px 0 0; font-size:13px; font-family:Arial, sans-serif;">Confidential · INV/HR/EIQ/v1.0</p>
        </td>
      </tr>
    </table>
    <div class="body">
      <p>Dear <strong>${employee_name}</strong>,</p>
      <div class="reminder-box">
        <p>⏳ We noticed you haven't completed your Exit Interview Questionnaire yet.</p>
      </div>
      <p>Your feedback is important to us and helps Invenger improve the workplace
         for future employees. The form takes only 10–15 minutes to complete.</p>
      <p>Please click the button below to complete it at your earliest convenience:</p>
      <a href="${form_link}" class="btn">Complete Exit Interview Now</a>
      <p style="font-size:13px; color:#6b7280;">
        Or copy this link: <br>
        <span style="color:#d97706;">${form_link}</span>
      </p>
      <p>Thank you for your time, and we wish you all the best in your future endeavours.</p>
      <p>Warm regards,<br><strong>Invenger HR Team</strong></p>
      <img src="cid:invengerlogo" alt="Invenger" width="70" height="18" style="height:18px; width:70px; margin-top:10px; display:block;" />
    </div>
    <div class="footer">
      <p>Invenger Technologies &nbsp;·&nbsp; Confidential HR Communication</p>
      <p>Doc: INV/HR/EIQ/v1.0</p>
    </div>
  </div>
</body>
</html>`;
}

function concernReminderTemplate({ employee_name, category, message, response_link }) {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 0; }
    .container { max-width: 600px; margin: 40px auto; background: #ffffff;
                 border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    .body { padding: 32px 40px; }
    .body p { color: #374151; font-size: 15px; line-height: 1.6; margin: 0 0 16px; }
    .reminder-box { background: #fffbeb; border: 1px solid #fde68a;
                border-radius: 8px; padding: 16px 20px; margin: 16px 0; }
    .reminder-box p { margin: 0; font-size: 14px; color: #92400e; font-weight: 600; }
    .category-badge { display: inline-block; background: #eff6ff; color: #1d4ed8;
                      border: 1px solid #bfdbfe; border-radius: 8px;
                      padding: 4px 12px; font-size: 13px; font-weight: 600;
                      text-transform: capitalize; margin-bottom: 16px; }
    .message-box { background: #f8fafc; border-left: 4px solid #2563eb;
                   border-radius: 0 8px 8px 0; padding: 16px 20px;
                   color: #374151; font-size: 14px; line-height: 1.6;
                   margin: 16px 0; }
    .btn { display: inline-block; background: #d97706; color: #ffffff !important;
           text-decoration: none; padding: 12px 28px; border-radius: 8px;
           font-weight: 700; font-size: 14px; margin: 20px 0; }
    .sign-logo { height: 18px; margin-top: 10px; }
    .footer { background: #f8fafc; padding: 20px 40px; text-align: center;
              color: #9ca3af; font-size: 12px; border-top: 1px solid #e5e7eb; }
  </style>
</head>
<body>
  <div class="container">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#d97706">
      <tr>
        <td align="center" style="padding:32px 40px; background-color:#d97706;">
          <p style="color:#ffffff; margin:0; font-size:20px; font-weight:700; font-family:Arial, sans-serif;">Reminder — Feedback Response Pending</p>
        </td>
      </tr>
    </table>
    <div class="body">
      <p>Dear <strong>${employee_name}</strong>,</p>
      <div class="reminder-box">
        <p>⏳ We noticed you haven't responded to HR's feedback request yet.</p>
      </div>
      <span class="category-badge">${category}</span>
      <div class="message-box">${message}</div>
      <p>Please take a moment to share your response — it is
         <strong>confidential</strong> and only visible to HR.</p>
      <a href="${response_link}" class="btn">Submit Your Response Now</a>
      <p style="font-size:13px; color:#6b7280;">
        Or copy this link: <br>
        <span style="color:#d97706;">${response_link}</span>
      </p>
      <p>Warm regards,<br><strong>Invenger HR Team</strong></p>
      <img src="cid:invengerlogo" alt="Invenger" width="70" height="18" style="height:18px; width:70px; margin-top:10px; display:block;" />
    </div>
    <div class="footer">
      <p>Invenger Technologies &nbsp;·&nbsp; This is a confidential HR communication.</p>
      <p>Please do not forward this email.</p>
    </div>
  </div>
</body>
</html>`;
}

// ── Reminder Routes ───────────────────────────────────────────────────────────
app.post("/send-exit-interview-reminder", async (req, res) => {
  const { employee_name, employee_email, form_link } = req.body;

  if (!employee_email) {
    return res.status(400).json({ error: "employee_email is required" });
  }

  try {
    await transporter.sendMail({
      from: `"${process.env.FROM_NAME}" <${process.env.SMTP_USER}>`,
      to: employee_email,
      subject: "Reminder — Please Complete Your Exit Interview | Invenger",
      html: exitInterviewReminderTemplate({ employee_name, form_link }),
      attachments: [logoAttachment],
    });

    console.log(`[REMINDER] Exit interview reminder sent to ${employee_email}`);
    res.json({ success: true, message: `Reminder sent to ${employee_email}` });
  } catch (err) {
    console.error("[REMINDER] Exit interview reminder failed:", err.message);
    res.status(500).json({ error: err.message });
  }
});

app.post("/send-concern-reminder", async (req, res) => {
  const { employee_name, employee_email, category, message, response_link } = req.body;

  if (!employee_email) {
    return res.status(400).json({ error: "employee_email is required" });
  }

  try {
    await transporter.sendMail({
      from: `"${process.env.FROM_NAME}" <${process.env.SMTP_USER}>`,
      to: employee_email,
      subject: `Reminder — Feedback Response Needed | Invenger`,
      html: concernReminderTemplate({ employee_name, category, message, response_link }),
      attachments: [logoAttachment],
    });

    console.log(`[REMINDER] Feedback reminder sent to ${employee_email}`);
    res.json({ success: true, message: `Reminder sent to ${employee_email}` });
  } catch (err) {
    console.error("[REMINDER] Feedback reminder failed:", err.message);
    res.status(500).json({ error: err.message });
  }
});

// ── Error handler — catches payload-too-large and other body-parser errors ──
app.use((err, req, res, next) => {
  if (err.type === "entity.too.large") {
    console.error("[ERROR] Payload too large:", err.message);
    return res.status(413).json({
      error: "Request payload too large. The photo may be too large to process.",
    });
  }
  console.error("[ERROR] Unhandled:", err.message);
  res.status(500).json({ error: "Internal server error" });
});

// ── Start server ──────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`✅ Email webhook running on http://localhost:${PORT}`);
  console.log(`   SMTP: ${process.env.SMTP_HOST}:${process.env.SMTP_PORT}`);
  console.log(`   From: ${process.env.SMTP_USER}`);
});