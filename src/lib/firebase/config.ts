import { initializeApp, getApps } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyDf5DmAtCTe95EegxQg2gEKky1KPjwMVEY",
  authDomain: "aistartupos.firebaseapp.com",
  projectId: "aistartupos",
  storageBucket: "aistartupos.firebasestorage.app",
  messagingSenderId: "783244568053",
  appId: "1:783244568053:web:10192ae0a894bee354acbc",
  measurementId: "G-6MH6P20037"
};

// Initialize Firebase
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
const auth = getAuth(app);
const db = getFirestore(app);

export { app, auth, db };
