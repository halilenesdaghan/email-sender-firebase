// functions/index.js (Revize Edilmiş Tam Hali)
const functions = require("firebase-functions");
const admin = require("firebase-admin");
const nodemailer = require("nodemailer");

admin.initializeApp();
const db = admin.firestore();

// --- DEĞİŞİKLİK 1: Güvenli Konfigürasyon ---
// Kimlik bilgileri koddan çıkarıldı. Bunları deploy ederken ayarlayacağız.
const gmailEmail = functions.config().gmail.email;
const gmailPassword = functions.config().gmail.password;

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
      const taskData = snap.data();
      const taskId = context.params.taskId; // Görev ID'sini alıyoruz.

      const mailOptions = {
        from: `Otomatik Servis <${gmailEmail}>`,
        to: taskData.recipient,
        subject: taskData.subject, // Python'dan gelen konu
        text: taskData.body,      // Python'dan gelen içerik
      };

      try {
        const info = await transporter.sendMail(mailOptions);
        console.log("E-posta başarıyla gönderildi:", info.response);

        // --- DEĞİŞİKLİK 3: Başarı Loglaması Eklendi ---
        return db.collection("email_logs").add({
          taskId: taskId, // Hangi göreve ait olduğu bilgisi
          recipient: taskData.recipient,
          status: "success",
          sentAt: admin.firestore.FieldValue.serverTimestamp(),
          response: info.response,
        });
      } catch (error) {
        console.error("E-posta gönderiminde hata:", error);

        // --- DEĞİŞİKLİK 3: Hata Loglaması Eklendi ---
        return db.collection("email_logs").add({
          taskId: taskId, // Hangi göreve ait olduğu bilgisi
          recipient: taskData.recipient,
          status: "error",
          failedAt: admin.firestore.FieldValue.serverTimestamp(),
          error: error.message, // Hatayı kaydet
        });
      }
    });