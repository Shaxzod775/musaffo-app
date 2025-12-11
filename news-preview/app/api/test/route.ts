import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const admin = require('firebase-admin');

    // Check if Firebase is initialized
    if (!admin.apps.length) {
      // Try environment variable first
      if (process.env.FIREBASE_SERVICE_ACCOUNT_KEY) {
        try {
          const serviceAccount = JSON.parse(
            Buffer.from(process.env.FIREBASE_SERVICE_ACCOUNT_KEY, 'base64').toString('utf-8')
          );
          admin.initializeApp({
            credential: admin.credential.cert(serviceAccount)
          });

          return NextResponse.json({
            status: 'success',
            message: 'Firebase initialized from ENV',
            hasEnv: true
          });
        } catch (e: any) {
          return NextResponse.json({
            status: 'error',
            message: 'Failed to parse ENV credentials',
            error: e.message,
            hasEnv: true
          });
        }
      } else {
        return NextResponse.json({
          status: 'error',
          message: 'No FIREBASE_SERVICE_ACCOUNT_KEY env variable',
          hasEnv: false,
          env: Object.keys(process.env).filter(k => k.includes('FIREBASE'))
        });
      }
    }

    return NextResponse.json({
      status: 'success',
      message: 'Firebase already initialized'
    });
  } catch (error: any) {
    return NextResponse.json({
      status: 'error',
      message: error.message
    });
  }
}
