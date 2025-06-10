document.addEventListener('DOMContentLoaded', function () {
  const forms = document.querySelectorAll('form.needs-success-msg');

  forms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      // הסרת הודעה קיימת
      const existing = document.querySelector('.form-success-msg');
      if (existing) existing.remove();

      // יצירת הודעה חדשה
      const msg = document.createElement('div');
      msg.classList.add('form-success-msg');
      msg.innerHTML = `
        <div class="msg-content">
          ✅ הטופס נשלח בהצלחה! <br> מעביר לדשבורד...
          <button id="closeSuccessMsg" title="סגור">✖️</button>
        </div>
      `;

      // סגנון כללי
      Object.assign(msg.style, {
        position: 'fixed',
        top: '30%',
        left: '50%',
        transform: 'translate(-50%, -30%)',
        backgroundColor: '#e6ffed',
        color: '#155724',
        border: '1px solid #a3d8af',
        padding: '20px 30px',
        borderRadius: '12px',
        textAlign: 'center',
        zIndex: 9999,
        fontSize: '18px',
        boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)',
        transition: 'opacity 0.5s ease',
        opacity: '1'
      });

      // כפתור סגירה
      const styleBtn = msg.querySelector('#closeSuccessMsg').style;
      Object.assign(styleBtn, {
        border: 'none',
        background: 'none',
        fontWeight: 'bold',
        fontSize: '18px',
        marginTop: '10px',
        cursor: 'pointer',
        color: '#155724'
      });

      msg.querySelector('#closeSuccessMsg').addEventListener('click', () => {
        msg.style.opacity = '0';
        setTimeout(() => msg.remove(), 500);
      });

      // הוספה לדף
      document.body.appendChild(msg);

      // סגירה אוטומטית + שליחה
      setTimeout(() => {
        msg.style.opacity = '0';
        setTimeout(() => {
          msg.remove();
          form.submit();
        }, 500);
      }, 2000);
    });
  });
});
