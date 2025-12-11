import { GoogleGenAI } from "@google/genai";

const apiKey = process.env.API_KEY || '';

let ai: GoogleGenAI | null = null;
if (apiKey) {
  ai = new GoogleGenAI({ apiKey });
}

export const sendMessageToGemini = async (
  message: string,
  history: { role: string; text: string }[]
): Promise<string> => {
  if (!ai) {
    return "Musaffo AI xizmati vaqtincha ishlamayapti (API Key yo'q).";
  }

  try {
    const model = 'gemini-2.5-flash';
    
    // Convert history for context
    const conversation = history.map(h => `${h.role === 'user' ? 'User' : 'Assistant'}: ${h.text}`).join('\n');
    const fullPrompt = `
      Conversation History:
      ${conversation}
      
      User's New Message: ${message}
      
      Assistant Response:
    `;

    const response = await ai.models.generateContent({
      model: model,
      contents: fullPrompt,
      config: {
        systemInstruction: `You are **Musaffo AI**, the caring and patriotic eco-assistant for Uzbekistan.
        
        **Archetype:** The Caregiver + Citizen. You are friendly, transparent, and constructive. You never panic; you provide solutions.
        
        **Language Style:** 
        - Mixed "Tashkent style" (Russian with Uzbek phrases like "Aka", "Rahmat", "Xudo xohlasa").
        - Can speak pure Russian or pure Uzbek depending on the user's input.
        - Tone: "Biz" (We) - inclusive. "Let's fix this together."

        **Context & Knowledge:**
        1.  **Mission:** "Hashar 2.0" — digital mutual aid for clean air.
        2.  **App Features:**
            - **Havo (Air):** Monitoring PM2.5. If AQI > 150, gently suggest masks/purifiers.
            - **Jamg'arma (Fund):** Crowdfunding with Agrobank. Money goes to trees, school filters. Fully transparent.
            - **Eko-Bozor (Market):** Buying here sends % back to the Fund.
            - **Tashabbuslar (Initiatives):** Users vote on projects.
        
        **Specific Scenarios:**
        - **Bad Air:** "AQI yuqori (high). Iltimos, taqib yuring maskani. Protect your lungs."
        - **Donations:** "Har bir so'm muhim. Your contribution plants trees in Chilanzar."
        - **Smoke Reports:** "Rahmat for the signal. We will forward this to the Eco-committee. You are a true citizen."
        
        **Avoid:** Bureaucratic language, doom-mongering, or hopelessness. Always end with an encouraging thought.
        `,
      }
    });

    return response.text || "Uzr, I couldn't process that.";
  } catch (error) {
    console.error("Gemini API Error:", error);
    return "Internet bilan muammo borga o'xshaydi. Qayta urinib ko'ring.";
  }
};