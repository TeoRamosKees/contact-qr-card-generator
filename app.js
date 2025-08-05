// vCard QR Generator - Pure JavaScript Implementation
class VCardQRGenerator {
  constructor() {
    this.form = document.getElementById("vcardForm");
    this.errorMessage = document.getElementById("errorMessage");
    this.resultContainer = document.getElementById("resultContainer");
    this.qrCanvas = document.getElementById("qrCode");
    this.downloadBtn = document.getElementById("downloadBtn");

    this.init();
  }

  init() {
    this.form.addEventListener("submit", (e) => this.handleSubmit(e));
    this.downloadBtn.addEventListener("click", () => this.downloadQR());
  }

  handleSubmit(e) {
    e.preventDefault();

    const formData = this.getFormData();

    if (!this.validateData(formData)) {
      return;
    }

    const vcard = this.createVCard(formData);
    this.generateQR(vcard);
  }

  getFormData() {
    return {
      firstName: document.getElementById("firstName").value.trim(),
      lastName: document.getElementById("lastName").value.trim(),
      phone: document.getElementById("phone").value.trim(),
      email: document.getElementById("email").value.trim(),
      organization: document.getElementById("organization").value.trim(),
      title: document.getElementById("title").value.trim(),
      website: document.getElementById("website").value.trim(),
      address: document.getElementById("address").value.trim(),
    };
  }

  validateData(data) {
    // Check required fields
    const requiredFields = ["firstName", "lastName", "phone", "email"];

    for (const field of requiredFields) {
      if (!data[field]) {
        this.showError(
          `Please fill in ${field.replace(/([A-Z])/g, " $1").toLowerCase()}`
        );
        return false;
      }
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
      this.showError("Please enter a valid email address");
      return false;
    }

    this.hideError();
    return true;
  }

  createVCard(data) {
    const vcard = [
      "BEGIN:VCARD",
      "VERSION:3.0",
      `FN:${data.firstName} ${data.lastName}`,
      `N:${data.lastName};${data.firstName};;;`,
      data.organization ? `ORG:${data.organization}` : "",
      data.title ? `TITLE:${data.title}` : "",
      `TEL:${data.phone}`,
      `EMAIL:${data.email}`,
      data.website ? `URL:${data.website}` : "",
      data.address ? `ADR:;;${data.address};;;;` : "",
      "END:VCARD",
    ]
      .filter((line) => line !== "")
      .join("\n");

    return vcard;
  }

  generateQR(vcard) {
    try {
      // Create QR code using QRious library
      const qr = new QRious({
        element: this.qrCanvas,
        value: vcard,
        size: 250,
        level: "M",
      });

      this.showResult();
    } catch (error) {
      this.showError("Error generating QR code: " + error.message);
    }
  }

  downloadQR() {
    // Create download link
    const canvas = this.qrCanvas;
    const link = document.createElement("a");
    link.download = "vcard-qr-code.png";
    link.href = canvas.toDataURL();
    link.click();
  }

  showError(message) {
    this.errorMessage.textContent = message;
    this.errorMessage.style.display = "block";
    this.resultContainer.style.display = "none";
  }

  hideError() {
    this.errorMessage.style.display = "none";
  }

  showResult() {
    this.resultContainer.style.display = "block";
    this.hideError();
  }
}

// Initialize the app when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new VCardQRGenerator();
});
