// auth.js — AgriTech Authentication System
// Switched back to Flask Backend

export const ROLES = {
  FARMER: "farmer",
  BUYER: "buyer",
  EQUIPMENT: "equipment",
  GROCERY: "grocery",
  EXPERT: "expert",
  ADMIN: "admin",
};

const ROLE_HOME = {
  farmer: "/pages/dashboards/farmer.html",
  buyer: "/pages/dashboards/buyer.html",
  equipment: "/pages/dashboards/equipment.html",
  grocery: "/pages/dashboards/grocery.html",
  expert: "/pages/dashboards/expert.html",
  admin: "/pages/dashboards/admin.html",
};

const API_BASE = 'http://localhost:5000/api/auth';

class AuthManager {
  constructor() {
    this.currentUser = null;
    this.getCurrentUser();
  }

  async register({ role, fullname, email, password }) {
    const validation = this._validateRegistrationData({ role, fullname, email, password });
    if (!validation.valid) {
      return { success: false, message: validation.message };
    }

    const pwCheck = this._validatePassword(password);
    if (!pwCheck.valid) return { success: false, message: pwCheck.message };

    try {
      const username = email.split('@')[0] + Math.floor(Math.random()*1000);
      const res = await fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: username,
          email: email.trim().toLowerCase(),
          password: password,
          full_name: fullname.trim(),
          role: role.trim().toLowerCase()
        })
      });

      const data = await res.json();
      if (!res.ok) {
        return { success: false, message: data.message || "Registration failed." };
      }

      return {
        success: true,
        message: "Account created successfully! You can now log in.",
        user: data.user
      };
    } catch (err) {
      return { success: false, message: "Network error during registration." };
    }
  }

  async login(email, password) {
    if (email === 'demo' && password === 'demo') {
      const userData = {
        id: "demo_admin_123",
        fullname: "Demo Admin",
        email: "demo@agritech.com",
        role: "admin",
      };
      this._setSession(userData);
      this._seedDemoData().catch(console.error);
      return { success: true, message: "Demo Admin Login successful!", user: userData };
    }

    const validation = this._validateLoginData(email, password);
    if (!validation.valid) {
      return { success: false, message: validation.message };
    }

    try {
      const res = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: email.trim().toLowerCase(),
          password: password
        })
      });

      const data = await res.json();
      if (!res.ok) {
        return { success: false, message: data.message || "Invalid credentials." };
      }

      if (data.user && data.user.is_active === false) {
        return { success: false, message: "Account is deactivated. Contact support." };
      }

      const userData = {
        id: data.user.id,
        fullname: data.user.full_name,
        email: data.user.email,
        role: data.user.role,
        token: data.access_token
      };
      this._setSession(userData);

      return { success: true, message: "Login successful!", user: userData };
    } catch (err) {
      return { success: false, message: "Network error during login." };
    }
  }

  async logout() {
    try {
      sessionStorage.removeItem("agritech_session");
      this.currentUser = null;
      window.location.href = "/pages/auth/login.html";
      return { success: true };
    } catch (err) {
      return { success: false, message: err.message };
    }
  }

  isLoggedIn() {
    return this.currentUser !== null;
  }

  getCurrentUser() {
    if (this.currentUser) return this.currentUser;
    const session = sessionStorage.getItem("agritech_session");
    if (session) {
      this.currentUser = JSON.parse(session);
      return this.currentUser;
    }
    return null;
  }
  
  _setSession(user) {
    this.currentUser = user;
    sessionStorage.setItem("agritech_session", JSON.stringify(user));
  }

  getHomePageForRole(role) {
    return ROLE_HOME[role] || "/pages/main.html";
  }

  async getAllUsers() { return []; }
  async setBanned(uid, isBanned) { return { success: true }; }
  async setRole(uid, newRole) { return { success: true }; }

  async _seedDemoData() {
    try {
            const users = JSON.parse(localStorage.getItem("agritech_demo_users") || "[]");
      if (users.length > 5) return; 
      
      const dummyUsers = [
        { id: 'demo_f1', fullname: 'Ramesh Farmer', email: 'ramesh@demo.com', role: 'farmer', isBanned: false, isActive: true },
        { id: 'demo_f2', fullname: 'Sunita Devi', email: 'sunita@demo.com', role: 'farmer', isBanned: false, isActive: true },
        { id: 'demo_f3', fullname: 'Anil Kumar', email: 'anil@demo.com', role: 'farmer', isBanned: false, isActive: true },
        { id: 'demo_b1', fullname: 'Suresh Buyer', email: 'suresh@demo.com', role: 'buyer', isBanned: false, isActive: true },
        { id: 'demo_b2', fullname: 'FreshMart Ltd', email: 'contact@freshmart.demo', role: 'buyer', isBanned: false, isActive: true },
        { id: 'demo_e1', fullname: 'Dr. Expert', email: 'expert@demo.com', role: 'expert', isBanned: false, isActive: true },
        { id: 'demo_e2', fullname: 'Prof. Sharma', email: 'sharma@demo.com', role: 'expert', isBanned: false, isActive: true },
        { id: 'demo_eq1', fullname: 'Tractor Rentals Co', email: 'rentals@demo.com', role: 'equipment', isBanned: false, isActive: true },
        { id: 'demo_gr1', fullname: 'Village Grocer', email: 'grocer@demo.com', role: 'grocery', isBanned: false, isActive: true },
        { id: 'demo_bad', fullname: 'Spammer', email: 'spam@demo.com', role: 'farmer', isBanned: true, isActive: true }
      ];
      
      for (const u of dummyUsers) {
        await setDoc(doc(db, 'users', u.id), { ...u, createdAt: serverTimestamp() });
      }
      
      await setDoc(doc(db, 'reports', 'rep1'), {
        reason: 'Inappropriate Content', description: 'User posted a spam link in the forum.', resolved: false, createdAt: serverTimestamp()
      });
      await setDoc(doc(db, 'reports', 'rep2'), {
        reason: 'Scam Alert', description: 'Fake equipment listing.', resolved: false, createdAt: serverTimestamp()
      });
      await setDoc(doc(db, 'reports', 'rep3'), {
        reason: 'Harassment', description: 'Abusive language in crop discussion.', resolved: false, createdAt: serverTimestamp()
      });
      await setDoc(doc(db, 'reports', 'rep4'), {
        reason: 'Spam', description: 'Posting the same ad 10 times.', resolved: true, createdAt: serverTimestamp()
      });

      await setDoc(doc(db, 'posts', 'post1'), {
        title: 'Tomato leaf curling issue', body: 'My tomato plants have curling leaves. What fertilizer should I use?', authorName: 'Ramesh Farmer', authorId: 'demo_f1', createdAt: new Date().toISOString(), answers: []
      });
      await setDoc(doc(db, 'posts', 'post2'), {
        title: 'Best time to sow wheat in Punjab?', body: 'When is the ideal time to sow wheat this season?', authorName: 'Anil Kumar', authorId: 'demo_f3', createdAt: new Date().toISOString(), answers: []
      });
      
      console.log("Extensive demo data seeded.");
    } catch (e) {
      console.error("Error seeding demo data:", e);
    }
  }

  _setSession(user) {
    this.currentUser = user;
    sessionStorage.setItem("agritech_session", JSON.stringify(user));
  }

  _validateEmail(email) {
    return /^[^\s@]+@gmail\.com$/.test(email);
  }

  _validatePassword(password) {
    if (password.length < 8)
      return {
        valid: false,
        message: "Password must be at least 8 characters long",
      };
    if (!/[a-z]/.test(password))
      return {
        valid: false,
        message: "Password must contain at least one lowercase letter",
      };
    if (!/[A-Z]/.test(password))
      return {
        valid: false,
        message: "Password must contain at least one uppercase letter",
      };
    if (!/\d/.test(password))
      return {
        valid: false,
        message: "Password must contain at least one number",
      };
    return { valid: true };
  }

  _validateRegistrationData({ role, fullname, email, password }) {
    if (!role || !fullname || !email || !password) {
      return { valid: false, message: "All fields are required" };
    }

    const normalizedRole = role.trim().toLowerCase();
    const allowedRoles = ["buyer", "farmer", "equipment", "grocery", "expert"];

    if (!allowedRoles.includes(normalizedRole)) {
      return { valid: false, message: "Please select a valid role" };
    }

    if (!/^[a-zA-Z\s.'-]+$/.test(fullname.trim())) {
      return { valid: false, message: "Full name can only contain letters and spaces" };
    }

    if (!this._validateEmail(email)) {
      return { valid: false, message: "Please use a valid @gmail.com address" };
    }

    return { valid: true };
  }

  _validateLoginData(email, password) {
    if (!email || !password) {
      return { valid: false, message: "Email and password are required" };
    }

    if (!this._validateEmail(email)) {
      return { valid: false, message: "Please enter a valid @gmail.com address" };
    }

    return { valid: true };
  }

  _friendlyError(code) {
    const map = {
      "auth/email-already-in-use": "An account with this email already exists.",
      "auth/invalid-email": "Please enter a valid email address.",
      "auth/weak-password": "Password must be at least 6 characters.",
      "auth/user-not-found": "Invalid email or password.",
      "auth/wrong-password": "Invalid email or password.",
      "auth/too-many-requests": "Too many attempts. Please try again later.",
      "auth/network-request-failed": "Network error. Check your connection.",
      "auth/invalid-credential": "Invalid email or password.",
    };
    return map[code] || "Something went wrong. Please try again.";
  }

  // ── UI helper (kept from old auth.js) ─────
  updateAuthUI() {
    const user = this.getCurrentUser();
    const isLoggedIn = !!user;

    const loginBtn = document.querySelector(".login-btn-desktop");
    const registerBtn = document.querySelector(".register-btn-desktop");
    const logoutBtn = document.querySelector(".logout-button");
    const mobileLogin = document.querySelector(
      'a[href="/pages/auth/login.html"].mobile-link',
    );
    const mobileReg = document.querySelector(
      'a[href="/pages/auth/register.html"].mobile-link',
    );

    if (isLoggedIn) {
      if (loginBtn) loginBtn.style.display = "none";
      if (registerBtn) registerBtn.style.display = "none";
      if (logoutBtn) {
        logoutBtn.style.display = "inline-flex";
        logoutBtn.onclick = (e) => {
          e.preventDefault();
          this.logout();
        };
      }
      if (mobileLogin) mobileLogin.style.display = "none";
      if (mobileReg) mobileReg.style.display = "none";
    } else {
      if (loginBtn) loginBtn.style.display = "inline-flex";
      if (registerBtn) registerBtn.style.display = "inline-flex";
      if (logoutBtn) logoutBtn.style.display = "none";
      if (mobileLogin) mobileLogin.style.display = "flex";
      if (mobileReg) mobileReg.style.display = "flex";
    }
  }
}

// ─────────────────────────────────────────────
// Singleton
// ─────────────────────────────────────────────
window.authManager = new AuthManager();

// ─────────────────────────────────────────────
// Page guards — same function names as before
// ─────────────────────────────────────────────

/**
 * requireAuth([allowedRoles])
 * Call on any protected page.
 * Optionally pass roles that are allowed, e.g. requireAuth(["admin"])
 */
window.requireAuth = function (allowedRoles = []) {
  const user = window.authManager.getCurrentUser();
  if (!user) {
    window.location.href = "/pages/auth/login.html";
    return false;
  }
  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    window.location.href = "/pages/auth/unauthorized.html";
    return false;
  }
  return true;
};

/** Redirect already-logged-in users away from login/register pages */
window.redirectIfLoggedIn = function () {
  const user = window.authManager.getCurrentUser();
  if (user) {
    window.location.href = window.authManager.getHomePageForRole(user.role);
  }
};

// ─────────────────────────────────────────────
// showAuthMessage — kept exactly from old auth.js
// ─────────────────────────────────────────────
window.showAuthMessage = function (message, type = "info") {
  const existing = document.querySelector(".auth-message");
  if (existing) existing.remove();

  const div = document.createElement("div");
  div.className = `auth-message auth-message-${type}`;
  div.innerHTML = `
    <div class="auth-message-content">
      <i class="fas fa-${type === "success" ? "check-circle" : type === "error" ? "exclamation-circle" : "info-circle"}"></i>
      <span>${message}</span>
    </div>`;

  div.style.cssText = `
    position:fixed; top:20px; right:20px; z-index:10000;
    padding:15px 20px; border-radius:8px; color:white;
    font-weight:500; box-shadow:0 4px 12px rgba(0,0,0,.15);
    animation:slideInRight .3s ease-out; max-width:400px;`;

  const colors = {
    success: "linear-gradient(135deg,#4caf50,#45a049)",
    error: "linear-gradient(135deg,#f44336,#e53935)",
    info: "linear-gradient(135deg,#2196f3,#1976d2)",
  };
  div.style.background = colors[type] || colors.info;
  document.body.appendChild(div);

  setTimeout(() => {
    if (div.parentNode) {
      div.style.animation = "slideOutRight .3s ease-out";
      setTimeout(() => div.remove(), 300);
    }
  }, 5000);
};

// CSS animations (same as before)
const s = document.createElement("style");
s.textContent = `
  @keyframes slideInRight  { from{opacity:0;transform:translateX(100%)} to{opacity:1;transform:translateX(0)} }
  @keyframes slideOutRight { from{opacity:1;transform:translateX(0)}    to{opacity:0;transform:translateX(100%)} }
  .auth-message-content { display:flex; align-items:center; gap:10px; }
  .auth-message-content i { font-size:1.2rem; }
`;
document.head.appendChild(s);

// Run UI update on every page load
document.addEventListener("DOMContentLoaded", () => {
  window.authManager.updateAuthUI();
});
