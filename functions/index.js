// functions/index.js (Revize Edilmiş Tam Hali)
const functions = require("firebase-functions");
const admin = require("firebase-admin");
const nodemailer = require("nodemailer");

admin.initializeApp();
const db = admin.firestore();

// --- DEĞİŞİKLİK 1: Güvenli Konfigürasyon ---
// Kimlik bilgileri koddan çıkarıldı. Bunları deploy ederken ayarlayacağız.
const { gmail } = functions.config();
const gmailEmail = gmail ? gmail.email : undefined;
const gmailPassword = gmail ? gmail.password : undefined;

// Nodemailer için transporter nesnesini oluştur
const transporter = nodemailer.createTransport({
  service: "gmail",
  auth: {
    user: gmailEmail,
    pass: gmailPassword,
  },
});

// --- DEĞİŞİKLİK 2: Doğru Koleksiyon Adı ---
// Fonksiyon artık Python'un yazdığı 'email_tasks' koleksiyonunu dinliyor.
exports.sendEmailOnTaskCreate = functions.firestore
  .document("email_tasks/{taskId}")
  .onCreate(async (snap, context) => {
    try {
      const taskData = snap.data();
      if (!taskData) {
        throw new Error("Görev verisi tanımsız");
      }

      const { recipient, subject, body } = taskData;
      const mailOptions = {
        from: `Otomatik Servis <${gmailEmail}>`,
        to: recipient,
        subject,
        text: body,
      };

      const info = await transporter.sendMail(mailOptions);
      await db.collection("email_logs").add({
        taskId: context.params.taskId,
        recipient,
        status: "success",
        sentAt: admin.firestore.FieldValue.serverTimestamp(),
        response: info.response,
      });
    } catch (error) {
      console.error("E-posta gönderiminde hata:", error);
      await db.collection("email_logs").add({
        taskId: context.params.taskId,
        recipient: snap.data()?.recipient,
        status: "error",
        failedAt: admin.firestore.FieldValue.serverTimestamp(),
        error: error.message,
      });
    }
  });
