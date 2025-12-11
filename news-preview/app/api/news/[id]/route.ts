import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const admin = require('firebase-admin');

    if (!admin.apps.length) {
      let credential;
      if (process.env.FIREBASE_SERVICE_ACCOUNT_KEY) {
        const serviceAccount = JSON.parse(
          Buffer.from(process.env.FIREBASE_SERVICE_ACCOUNT_KEY, 'base64').toString('utf-8')
        );
        credential = admin.credential.cert(serviceAccount);
      } else {
        // In production, FIREBASE_SERVICE_ACCOUNT_KEY should be set
        return NextResponse.json({ error: 'Firebase credentials not configured' }, { status: 500 });
      }

      admin.initializeApp({ credential });
    }

    const db = admin.firestore();
    const doc = await db.collection('news_preview').doc(id).get();

    if (!doc.exists) {
      return NextResponse.json({ error: 'News not found' }, { status: 404 });
    }

    const data = doc.data();

    // Return HTML with design matching the main app NewsDetail component
    const html = `
<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Новость о качестве воздуха</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @keyframes slide-up {
      from {
        transform: translateY(100%);
        opacity: 0;
      }
      to {
        transform: translateY(0);
        opacity: 1;
      }
    }
    .animate-slide-up {
      animation: slide-up 0.3s ease-out;
    }
    .language-content {
      display: none;
    }
    .language-content.active {
      display: block;
    }
  </style>
</head>
<body class="bg-white m-0 p-0">
  <div class="fixed inset-0 z-[100] bg-white flex flex-col animate-slide-up">
    <!-- Header Image -->
    <div class="relative h-64 w-full shrink-0">
      <img
        src="https://images.unsplash.com/photo-1621451537084-482c73073a0f?auto=format&fit=crop&q=80&w=800"
        class="w-full h-full object-cover"
        alt="Air Quality News"
      />
      <div class="absolute inset-0 bg-gradient-to-b from-black/30 to-transparent"></div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-6">
      <div class="flex gap-2 mb-4 flex-wrap">
        <span class="bg-[#40A7E3]/10 text-[#40A7E3] px-3 py-1 rounded-lg text-xs font-bold uppercase flex items-center gap-1">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
          Air Quality
        </span>
        <span class="bg-[#F3F4F6] text-[#9CA3AF] px-3 py-1 rounded-lg text-xs font-bold flex items-center gap-1">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          ${new Date(data.date).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })}
        </span>
        <span class="bg-[#F3F4F6] text-[#9CA3AF] px-3 py-1 rounded-lg text-xs font-medium flex items-center gap-1">
          ${data.channel}
        </span>
      </div>

      <!-- Language Tabs -->
      <div class="flex gap-2 mb-6 border-b border-[#E5E7EB] pb-3">
        <button onclick="switchLanguage('ru')" class="language-tab px-4 py-2 rounded-lg text-sm font-semibold transition-all bg-[#40A7E3] text-white" data-lang="ru">
          🇷🇺 Русский
        </button>
        <button onclick="switchLanguage('uz')" class="language-tab px-4 py-2 rounded-lg text-sm font-semibold transition-all bg-[#F3F4F6] text-[#1F2937] hover:bg-[#E5E7EB]" data-lang="uz">
          🇺🇿 O'zbekcha
        </button>
        <button onclick="switchLanguage('en')" class="language-tab px-4 py-2 rounded-lg text-sm font-semibold transition-all bg-[#F3F4F6] text-[#1F2937] hover:bg-[#E5E7EB]" data-lang="en">
          🇬🇧 English
        </button>
      </div>

      <!-- Content for each language -->
      <div class="prose prose-sm text-[#4B5563] max-w-none">
        <div class="language-content active" data-lang="ru">
          <p class="text-[#1F2937] leading-relaxed text-base whitespace-pre-wrap">${data.translations?.ru || data.text}</p>
        </div>
        <div class="language-content" data-lang="uz">
          <p class="text-[#1F2937] leading-relaxed text-base whitespace-pre-wrap">${data.translations?.uz || 'Tarjima mavjud emas'}</p>
        </div>
        <div class="language-content" data-lang="en">
          <p class="text-[#1F2937] leading-relaxed text-base whitespace-pre-wrap">${data.translations?.en || 'Translation not available'}</p>
        </div>
      </div>

      ${data.link ? `
      <div class="mt-8 pt-6 border-t border-[#E5E7EB]">
        <a href="${data.link}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-2 text-[#40A7E3] hover:text-[#3090D0] font-semibold text-sm">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          Открыть оригинал в Telegram
        </a>
      </div>
      ` : ''}
    </div>

    <!-- Footer -->
    <div class="p-4 border-t border-[#E5E7EB] bg-white">
      <p class="text-[#9CA3AF] text-xs text-center">
        🌍 Мониторинг качества воздуха Musaffo
      </p>
    </div>
  </div>

  <script>
    function switchLanguage(lang) {
      // Update tabs
      document.querySelectorAll('.language-tab').forEach(tab => {
        if (tab.dataset.lang === lang) {
          tab.classList.remove('bg-[#F3F4F6]', 'text-[#1F2937]', 'hover:bg-[#E5E7EB]');
          tab.classList.add('bg-[#40A7E3]', 'text-white');
        } else {
          tab.classList.remove('bg-[#40A7E3]', 'text-white');
          tab.classList.add('bg-[#F3F4F6]', 'text-[#1F2937]', 'hover:bg-[#E5E7EB]');
        }
      });

      // Update content
      document.querySelectorAll('.language-content').forEach(content => {
        if (content.dataset.lang === lang) {
          content.classList.add('active');
        } else {
          content.classList.remove('active');
        }
      });
    }
  </script>
</body>
</html>
    `;

    return new NextResponse(html, {
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
      },
    });
  } catch (error: any) {
    console.error('Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
