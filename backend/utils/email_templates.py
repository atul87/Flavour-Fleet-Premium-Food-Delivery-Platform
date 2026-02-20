# ============================================
# FLAVOUR FLEET — Email Templates
# ============================================
# Premium HTML email templates for transactional emails.


def order_confirmation_template(user_name, order_id, items_summary, total):
    """Email sent when a new order is placed."""
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;font-family:'Segoe UI',Arial,sans-serif;background:#f4f4f7;">
      <div style="max-width:600px;margin:40px auto;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

        <!-- Header -->
        <div style="background:linear-gradient(135deg,#ff6b35,#ff8c42);padding:32px;text-align:center;">
          <h1 style="margin:0;color:#fff;font-size:28px;">🔥 Flavour Fleet</h1>
          <p style="color:rgba(255,255,255,0.9);margin:8px 0 0;font-size:14px;">Delicious food, delivered fast</p>
        </div>

        <!-- Body -->
        <div style="padding:32px;">
          <h2 style="color:#1a1a2e;margin:0 0 8px;font-size:22px;">🍔 Order Confirmed!</h2>
          <p style="color:#555;font-size:15px;line-height:1.6;">
            Hi <strong>{user_name}</strong>,
          </p>
          <p style="color:#555;font-size:15px;line-height:1.6;">
            Your order has been confirmed and we're preparing your delicious meal!
          </p>

          <!-- Order Details Card -->
          <div style="background:#f8f9fa;border-radius:12px;padding:20px;margin:20px 0;border-left:4px solid #ff6b35;">
            <p style="margin:0 0 8px;color:#888;font-size:12px;text-transform:uppercase;letter-spacing:1px;">Order Details</p>
            <p style="margin:0 0 6px;color:#1a1a2e;font-size:16px;"><strong>Order ID:</strong> #{order_id}</p>
            <p style="margin:0 0 6px;color:#1a1a2e;font-size:16px;"><strong>Items:</strong> {items_summary}</p>
            <p style="margin:0;color:#ff6b35;font-size:22px;font-weight:700;">Total: ${total}</p>
          </div>

          <!-- Status Steps -->
          <div style="display:flex;justify-content:space-between;margin:24px 0;text-align:center;">
            <div style="flex:1;">
              <div style="width:36px;height:36px;background:#ff6b35;border-radius:50%;margin:0 auto 6px;line-height:36px;color:#fff;font-size:16px;">✓</div>
              <span style="font-size:11px;color:#888;">Confirmed</span>
            </div>
            <div style="flex:1;">
              <div style="width:36px;height:36px;background:#e0e0e0;border-radius:50%;margin:0 auto 6px;line-height:36px;color:#999;font-size:16px;">🍳</div>
              <span style="font-size:11px;color:#888;">Preparing</span>
            </div>
            <div style="flex:1;">
              <div style="width:36px;height:36px;background:#e0e0e0;border-radius:50%;margin:0 auto 6px;line-height:36px;color:#999;font-size:16px;">🚗</div>
              <span style="font-size:11px;color:#888;">On the way</span>
            </div>
            <div style="flex:1;">
              <div style="width:36px;height:36px;background:#e0e0e0;border-radius:50%;margin:0 auto 6px;line-height:36px;color:#999;font-size:16px;">🎉</div>
              <span style="font-size:11px;color:#888;">Delivered</span>
            </div>
          </div>

          <p style="color:#888;font-size:13px;line-height:1.5;margin-top:24px;">
            You'll receive another email when your order is on the way. Thank you for choosing Flavour Fleet! 🚀
          </p>
        </div>

        <!-- Footer -->
        <div style="background:#f8f9fa;padding:20px;text-align:center;border-top:1px solid #eee;">
          <p style="margin:0;color:#aaa;font-size:12px;">© 2026 Flavour Fleet. All rights reserved.</p>
          <p style="margin:4px 0 0;color:#ccc;font-size:11px;">You received this email because you placed an order.</p>
        </div>
      </div>
    </body>
    </html>
    """


def order_delivered_template(user_name, order_id):
    """Email sent when an order is marked as delivered."""
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;font-family:'Segoe UI',Arial,sans-serif;background:#f4f4f7;">
      <div style="max-width:600px;margin:40px auto;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

        <!-- Header -->
        <div style="background:linear-gradient(135deg,#00b894,#00cec9);padding:32px;text-align:center;">
          <h1 style="margin:0;color:#fff;font-size:28px;">🔥 Flavour Fleet</h1>
          <p style="color:rgba(255,255,255,0.9);margin:8px 0 0;font-size:14px;">Your meal has arrived!</p>
        </div>

        <!-- Body -->
        <div style="padding:32px;">
          <h2 style="color:#1a1a2e;margin:0 0 8px;font-size:22px;">🎉 Order Delivered!</h2>
          <p style="color:#555;font-size:15px;line-height:1.6;">
            Hi <strong>{user_name}</strong>,
          </p>
          <p style="color:#555;font-size:15px;line-height:1.6;">
            Great news! Your order <strong>#{order_id}</strong> has been delivered successfully.
          </p>

          <!-- Delivered Badge -->
          <div style="text-align:center;margin:28px 0;">
            <div style="display:inline-block;background:linear-gradient(135deg,#00b894,#00cec9);border-radius:50%;width:80px;height:80px;line-height:80px;font-size:40px;">
              ✅
            </div>
            <p style="color:#00b894;font-size:18px;font-weight:700;margin:12px 0 0;">Successfully Delivered</p>
          </div>

          <div style="background:#f8f9fa;border-radius:12px;padding:20px;margin:20px 0;text-align:center;">
            <p style="margin:0 0 8px;color:#888;font-size:13px;">How was your experience?</p>
            <div style="font-size:28px;letter-spacing:8px;">⭐ ⭐ ⭐ ⭐ ⭐</div>
            <p style="margin:8px 0 0;color:#aaa;font-size:12px;">Rate your order on the app</p>
          </div>

          <p style="color:#888;font-size:13px;line-height:1.5;margin-top:24px;">
            We hope you enjoyed your meal! Order again anytime at Flavour Fleet. 😋
          </p>
        </div>

        <!-- Footer -->
        <div style="background:#f8f9fa;padding:20px;text-align:center;border-top:1px solid #eee;">
          <p style="margin:0;color:#aaa;font-size:12px;">© 2026 Flavour Fleet. All rights reserved.</p>
        </div>
      </div>
    </body>
    </html>
    """


def password_reset_template(user_name, reset_code):
    """Email sent when a password reset is requested."""
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;font-family:'Segoe UI',Arial,sans-serif;background:#f4f4f7;">
      <div style="max-width:600px;margin:40px auto;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

        <!-- Header -->
        <div style="background:linear-gradient(135deg,#6c5ce7,#a29bfe);padding:32px;text-align:center;">
          <h1 style="margin:0;color:#fff;font-size:28px;">🔥 Flavour Fleet</h1>
          <p style="color:rgba(255,255,255,0.9);margin:8px 0 0;font-size:14px;">Account Security</p>
        </div>

        <!-- Body -->
        <div style="padding:32px;">
          <h2 style="color:#1a1a2e;margin:0 0 8px;font-size:22px;">🔐 Password Reset</h2>
          <p style="color:#555;font-size:15px;line-height:1.6;">
            Hi <strong>{user_name}</strong>,
          </p>
          <p style="color:#555;font-size:15px;line-height:1.6;">
            You requested a password reset for your Flavour Fleet account. Use the code below:
          </p>

          <!-- Reset Code Box -->
          <div style="text-align:center;margin:28px 0;">
            <div style="display:inline-block;background:linear-gradient(135deg,#6c5ce7,#a29bfe);border-radius:16px;padding:20px 40px;">
              <p style="margin:0 0 4px;color:rgba(255,255,255,0.8);font-size:12px;text-transform:uppercase;letter-spacing:2px;">Your Reset Code</p>
              <p style="margin:0;color:#fff;font-size:36px;font-weight:800;letter-spacing:8px;">{reset_code}</p>
            </div>
          </div>

          <div style="background:#fff3cd;border-radius:12px;padding:16px;margin:20px 0;border-left:4px solid #ffc107;">
            <p style="margin:0;color:#856404;font-size:13px;">
              ⏰ This code expires in <strong>15 minutes</strong>. If you didn't request this reset, please ignore this email — your account is safe.
            </p>
          </div>

          <p style="color:#888;font-size:13px;line-height:1.5;margin-top:24px;">
            For security, never share this code with anyone. Flavour Fleet team will never ask for your password or reset code.
          </p>
        </div>

        <!-- Footer -->
        <div style="background:#f8f9fa;padding:20px;text-align:center;border-top:1px solid #eee;">
          <p style="margin:0;color:#aaa;font-size:12px;">© 2026 Flavour Fleet Security Team</p>
        </div>
      </div>
    </body>
    </html>
    """
