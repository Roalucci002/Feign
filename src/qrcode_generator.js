const QRCode = require('qrcode');

class QRCodeGenerator {
  static async generate(text) {
    try {
      const qrCode = await QRCode.toDataURL(text, {
        errorCorrectionLevel: 'H',
        type: 'image/png',
        quality: 0.95,
        margin: 1,
        width: 300
      });
      return qrCode;
    } catch (err) {
      throw new Error(`QR Code generation failed: ${err.message}`);
    }
  }
}

module.exports = QRCodeGenerator;
