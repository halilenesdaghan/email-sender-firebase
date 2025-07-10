// functions/index.js
const functions = require('firebase-functions');
const admin = require('firebase-admin');
const nodemailer = require('nodemailer');

admin.initializeApp();

// Gmail SMTP ayarları
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'halilenesdaghan@gmail.com',
    pass: 'rmvxqhmuerfcmhro' // Gmail App Password
  }
});

// Firestore'a yeni email eklendiğinde tetiklenir
exports.sendEmail = functions.firestore
  .document('emails/{emailId}')
  .onCreate(async (snap, context) => {
    const emailData = snap.data();
    
    try {
      // E-posta gönder
      const mailOptions = {
        from: emailData.from || 'halilenesdaghan@gmail.com',
        to: emailData.to[0], // İlk alıcı
        subject: emailData.message.subject,
        text: emailData.message.text,
        html: emailData.message.html
      };
      
      const info = await transporter.sendMail(mailOptions);
      console.log('Email sent:', info.messageId);
      
      // Başarı durumunu güncelle
      await snap.ref.update({
        'delivery.state': 'SUCCESS',
        'delivery.endTime': admin.firestore.FieldValue.serverTimestamp(),
        'delivery.info': {
          messageId: info.messageId,
          response: info.response
        }
      });
      
      // Log kaydet
      await admin.firestore().collection('email_logs').add({
        recipient: emailData.to[0],
        subject: emailData.message.subject,
        status: 'success',
        timestamp: admin.firestore.FieldValue.serverTimestamp(),
        messageId: info.messageId
      });
      
    } catch (error) {
      console.error('Email sending failed:', error);
      
      // Hata durumunu güncelle
      await snap.ref.update({
        'delivery.state': 'ERROR',
        'delivery.error': error.message,
        'delivery.endTime': admin.firestore.FieldValue.serverTimestamp()
      });
      
      // Hata logu kaydet
      await admin.firestore().collection('email_logs').add({
        recipient: emailData.to[0],
        subject: emailData.message.subject,
        status: 'failed',
        error: error.message,
        timestamp: admin.firestore.FieldValue.serverTimestamp()
      });
    }
  });