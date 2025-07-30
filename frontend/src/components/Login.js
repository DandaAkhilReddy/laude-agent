import React, { useState, useEffect } from 'react';
import { Mail, Shield, Clock, AlertCircle, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

import { authService } from '../services/authService';
import LoadingSpinner from './LoadingSpinner';

const Login = ({ onLogin }) => {
  const [step, setStep] = useState('email'); // 'email' or 'otp'
  const [email, setEmail] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  const [resendAvailable, setResendAvailable] = useState(false);

  // OTP Timer
  useEffect(() => {
    let interval;
    if (timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft(timeLeft - 1);
      }, 1000);
    } else if (timeLeft === 0 && otpSent) {
      setResendAvailable(true);
    }
    return () => clearInterval(interval);
  }, [timeLeft, otpSent]);

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      toast.error('Please enter your email address');
      return;
    }

    if (!email.endsWith('@hssmedicine.com')) {
      toast.error('Access restricted to HSS Medicine employees only');
      return;
    }

    setLoading(true);
    try {
      const result = await authService.generateOTP(email.trim().toLowerCase());
      
      if (result.success) {
        setStep('otp');
        setOtpSent(true);
        setTimeLeft(600); // 10 minutes
        setResendAvailable(false);
        toast.success(`Verification code sent to ${email}`);
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Failed to send verification code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOtpSubmit = async (e) => {
    e.preventDefault();
    if (!otpCode.trim() || otpCode.length !== 6) {
      toast.error('Please enter the 6-digit verification code');
      return;
    }

    setLoading(true);
    try {
      const result = await onLogin(email.trim().toLowerCase(), otpCode.trim());
      
      if (!result.success) {
        toast.error(result.error);
        // Don't reset form on error, let user try again
      }
    } catch (error) {
      toast.error('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    if (!resendAvailable) return;
    
    setLoading(true);
    try {
      const result = await authService.generateOTP(email);
      
      if (result.success) {
        setTimeLeft(600);
        setResendAvailable(false);
        setOtpCode('');
        toast.success('New verification code sent!');
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Failed to resend code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleBackToEmail = () => {
    setStep('email');
    setOtpCode('');
    setOtpSent(false);
    setTimeLeft(0);
    setResendAvailable(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-hss-primary via-hss-secondary to-blue-600 flex items-center justify-center p-4">
      {/* Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-10 -left-10 w-72 h-72 bg-white opacity-5 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 -right-10 w-96 h-96 bg-white opacity-5 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-10 left-1/3 w-80 h-80 bg-white opacity-5 rounded-full blur-3xl"></div>
      </div>

      <div className="relative w-full max-w-md">
        {/* Main Login Card */}
        <div className="medical-card p-8 rounded-2xl shadow-medical-xl backdrop-blur-sm">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-hss-primary to-hss-secondary rounded-2xl mb-4 shadow-lg">
              <span className="text-2xl text-white">🎙️</span>
            </div>
            <h1 className="text-2xl font-bold text-hss-primary mb-2">Laude Agent</h1>
            <p className="text-gray-600">HSS Medicine Enterprise Platform</p>
          </div>

          {/* Email Step */}
          {step === 'email' && (
            <form onSubmit={handleEmailSubmit} className="space-y-6 animate-fade-in">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Corporate Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="form-input-focus block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none text-gray-900 placeholder-gray-500"
                    placeholder="yourname@hssmedicine.com"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Domain Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start">
                  <Shield className="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
                  <div>
                    <h4 className="text-sm font-medium text-blue-800 mb-1">
                      🔒 Secure Access
                    </h4>
                    <ul className="text-sm text-blue-700 space-y-1">
                      <li>• Only @hssmedicine.com employees</li>
                      <li>• OTP verification required</li>
                      <li>• Enterprise-grade security</li>
                    </ul>
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading || !email.trim()}
                className="medical-button w-full py-3 px-4 text-white font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-hss-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <LoadingSpinner size="sm" color="white" className="mr-2" />
                    Sending Code...
                  </>
                ) : (
                  'Continue with Email'
                )}
              </button>
            </form>
          )}

          {/* OTP Step */}
          {step === 'otp' && (
            <form onSubmit={handleOtpSubmit} className="space-y-6 animate-fade-in">
              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mb-3">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Email Verification
                </h3>
                <p className="text-sm text-gray-600">
                  Enter the 6-digit code sent to<br />
                  <span className="font-medium text-hss-primary">{email}</span>
                </p>
              </div>

              <div>
                <label htmlFor="otpCode" className="block text-sm font-medium text-gray-700 mb-2">
                  Verification Code
                </label>
                <input
                  id="otpCode"
                  type="text"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  className="form-input-focus block w-full px-3 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none text-center text-2xl tracking-widest font-mono text-gray-900"
                  placeholder="123456"
                  maxLength={6}
                  required
                  disabled={loading}
                  autoFocus
                />
              </div>

              {/* Timer */}
              <div className="text-center">
                {timeLeft > 0 ? (
                  <div className="flex items-center justify-center text-sm text-gray-600">
                    <Clock className="h-4 w-4 mr-2" />
                    Code expires in: <span className="font-mono ml-1">{formatTime(timeLeft)}</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center text-sm text-red-600">
                    <AlertCircle className="h-4 w-4 mr-2" />
                    Code expired
                  </div>
                )}
              </div>

              <button
                type="submit"
                disabled={loading || !otpCode.trim() || otpCode.length !== 6}
                className="medical-button w-full py-3 px-4 text-white font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-hss-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <LoadingSpinner size="sm" color="white" className="mr-2" />
                    Verifying...
                  </>
                ) : (
                  'Verify & Login'
                )}
              </button>

              {/* Resend / Back options */}
              <div className="flex items-center justify-between text-sm">
                <button
                  type="button"
                  onClick={handleBackToEmail}
                  className="text-gray-600 hover:text-hss-primary transition-colors"
                  disabled={loading}
                >
                  ← Change Email
                </button>
                
                <button
                  type="button"
                  onClick={handleResendOtp}
                  className={`transition-colors ${
                    resendAvailable && !loading
                      ? 'text-hss-primary hover:text-hss-secondary'
                      : 'text-gray-400 cursor-not-allowed'
                  }`}
                  disabled={!resendAvailable || loading}
                >
                  {loading ? 'Sending...' : 'Resend Code'}
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-white/80">
          <p className="text-sm">
            <strong>HSS Medicine</strong> - Laude Agent Enterprise
          </p>
          <p className="text-xs mt-1 text-white/60">
            Secure voice-to-email automation platform
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;