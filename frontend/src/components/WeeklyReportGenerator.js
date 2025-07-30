import React, { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Mic, 
  Square, 
  Play, 
  Pause, 
  FileText, 
  Send, 
  Download,
  Copy,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader
} from 'lucide-react';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';

import { apiService } from '../services/apiService';
import LoadingSpinner from './LoadingSpinner';

const WeeklyReportGenerator = ({ user, onLogout }) => {
  const [step, setStep] = useState('record'); // 'record', 'transcript', 'report', 'email'
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [editedTranscript, setEditedTranscript] = useState('');
  const [report, setReport] = useState('');
  const [loading, setLoading] = useState(false);
  const [processingStep, setProcessingStep] = useState('');

  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const timerRef = useRef(null);
  const audioRef = useRef(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  // Recording timer
  useEffect(() => {
    if (isRecording && !isPaused) {
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isRecording, isPaused]);

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        }
      });
      
      streamRef.current = stream;
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      const chunks = [];
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingTime(0);
      toast.success('🎙️ Recording started! Speak clearly.');
    } catch (error) {
      console.error('Recording error:', error);
      toast.error('Failed to start recording. Please check microphone permissions.');
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume();
        setIsPaused(false);
        toast.success('Recording resumed');
      } else {
        mediaRecorderRef.current.pause();
        setIsPaused(true);
        toast.success('Recording paused');
      }
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      toast.success('Recording completed!');
    }
  };

  const transcribeAudio = async () => {
    if (!audioBlob) {
      toast.error('No audio recording found');
      return;
    }

    setLoading(true);
    setProcessingStep('Transcribing audio...');

    try {
      // For demo purposes, we'll simulate transcription
      // In production, you'd upload to backend and use Whisper API
      
      const simulatedTranscript = `This week at HSS Medicine, I made significant progress on several key healthcare technology initiatives.

I completed the implementation of the new patient management system which has already improved our workflow efficiency by approximately 30%. The system now includes enhanced HIPAA-compliant data handling and automated appointment scheduling features.

I also worked on upgrading our telemedicine platform security protocols, ensuring all patient video consultations meet the latest security standards. This included implementing end-to-end encryption and multi-factor authentication for healthcare providers.

Additionally, I resolved three critical system vulnerabilities that were identified during our security audit last week. These fixes have strengthened our overall cybersecurity posture significantly.

For training and development, I conducted two training sessions for our nursing staff on the new patient portal features, helping them become more proficient with the digital tools.

Looking ahead to next week, I plan to focus on launching the beta version of our mobile patient app, which will allow patients to access their medical records and schedule appointments directly from their smartphones.

I also need to complete the integration testing for our new insurance verification system, which should reduce administrative overhead for our billing department.

Key metrics for this week include: 30% improvement in workflow efficiency, zero security incidents since implementing the new protocols, 100% completion rate for planned security updates, and positive feedback from 25 staff members who attended the training sessions.

One challenge I encountered was a database migration issue, but I was able to resolve it by collaborating with our DevOps team and implementing a rollback strategy that minimized downtime to less than 10 minutes.`;

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setTranscript(simulatedTranscript);
      setEditedTranscript(simulatedTranscript);
      setStep('transcript');
      toast.success('Transcription completed!');
    } catch (error) {
      console.error('Transcription error:', error);
      toast.error('Failed to transcribe audio. Please try again.');
    } finally {
      setLoading(false);
      setProcessingStep('');
    }
  };

  const generateReport = async () => {
    if (!editedTranscript.trim()) {
      toast.error('Please provide transcript content');
      return;
    }

    setLoading(true);
    setProcessingStep('Generating professional report...');

    try {
      const result = await apiService.reports.generate(editedTranscript);
      
      if (result.success) {
        setReport(result.data.report_content);
        setStep('report');
        toast.success('Professional report generated! 📊');
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      console.error('Report generation error:', error);
      toast.error('Failed to generate report. Please try again.');
    } finally {
      setLoading(false);
      setProcessingStep('');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      toast.success('Copied to clipboard!');
    }).catch(() => {
      toast.error('Failed to copy to clipboard');
    });
  };

  const downloadReport = () => {
    if (!report) return;
    
    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `weekly-report-${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Report downloaded!');
  };

  const resetProcess = () => {
    setStep('record');
    setIsRecording(false);
    setIsPaused(false);
    setRecordingTime(0);
    setAudioBlob(null);
    setTranscript('');
    setEditedTranscript('');
    setReport('');
    setLoading(false);
    setProcessingStep('');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="healthcare-gradient shadow-medical-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Link
                to="/dashboard"
                className="bg-white/20 hover:bg-white/30 text-white p-2 rounded-lg mr-4 transition-colors"
              >
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <div>
                <h1 className="text-xl font-bold text-white">🎙️ Weekly Report Generator</h1>
                <p className="text-white/80 text-sm">AI-powered voice to professional report</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-white/80">{user?.full_name}</span>
              <button
                onClick={onLogout}
                className="bg-red-500/20 hover:bg-red-500/30 border border-red-400/30 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Indicator */}
        <div className="medical-card p-6 rounded-xl mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-hss-primary">Process Steps</h2>
            <button
              onClick={resetProcess}
              className="text-gray-500 hover:text-red-500 text-sm transition-colors"
            >
              Reset Process
            </button>
          </div>
          <div className="flex items-center space-x-4">
            {[
              { key: 'record', label: 'Record', icon: Mic },
              { key: 'transcript', label: 'Transcript', icon: FileText },
              { key: 'report', label: 'Report', icon: CheckCircle },
            ].map((stepItem, index) => {
              const Icon = stepItem.icon;
              const isActive = step === stepItem.key;
              const isCompleted = ['record', 'transcript', 'report'].indexOf(step) > index;
              
              return (
                <React.Fragment key={stepItem.key}>
                  <div className="flex items-center">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      isCompleted 
                        ? 'bg-green-100 text-green-600' 
                        : isActive 
                        ? 'bg-blue-100 text-blue-600' 
                        : 'bg-gray-100 text-gray-400'
                    }`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <span className={`ml-2 text-sm font-medium ${
                      isCompleted 
                        ? 'text-green-600' 
                        : isActive 
                        ? 'text-blue-600' 
                        : 'text-gray-400'
                    }`}>
                      {stepItem.label}
                    </span>
                  </div>
                  {index < 2 && (
                    <div className={`flex-1 h-1 rounded-full ${
                      isCompleted ? 'bg-green-200' : 'bg-gray-200'
                    }`} />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="medical-card p-8 rounded-xl mb-8 text-center">
            <LoadingSpinner size="lg" color="hss" className="mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-hss-primary mb-2">Processing</h3>
            <p className="text-gray-600">{processingStep}</p>
          </div>
        )}

        {/* Step 1: Recording */}
        {step === 'record' && (
          <div className="medical-card p-8 rounded-xl animate-fade-in">
            <div className="text-center">
              <div className="mb-8">
                <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full mb-6 ${
                  isRecording 
                    ? 'bg-red-100 animate-pulse' 
                    : 'bg-blue-100'
                }`}>
                  {isRecording ? (
                    <div className="relative">
                      <Square className="h-16 w-16 text-red-600" />
                      <div className="absolute inset-0 animate-ping">
                        <Square className="h-16 w-16 text-red-400 opacity-75" />
                      </div>
                    </div>
                  ) : (
                    <Mic className="h-16 w-16 text-blue-600" />
                  )}
                </div>
                
                <h3 className="text-2xl font-bold text-hss-primary mb-3">
                  {isRecording ? 'Recording in Progress' : 'Ready to Record'}
                </h3>
                
                {isRecording ? (
                  <div className="space-y-4">
                    <p className="text-gray-600">
                      {isPaused ? '⏸️ Recording paused' : '🎙️ Speak clearly about your weekly accomplishments'}
                    </p>
                    <div className="text-3xl font-mono text-red-600">
                      {formatTime(recordingTime)}
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-600 max-w-md mx-auto">
                    Click the microphone to start recording your weekly update. Speak naturally about your accomplishments, projects, and plans.
                  </p>
                )}
              </div>

              {/* Recording Controls */}
              <div className="flex items-center justify-center space-x-4">
                {!isRecording ? (
                  <button
                    onClick={startRecording}
                    className="medical-button px-8 py-4 text-white font-medium rounded-xl flex items-center text-lg"
                  >
                    <Mic className="h-6 w-6 mr-3" />
                    Start Recording
                  </button>
                ) : (
                  <>
                    <button
                      onClick={pauseRecording}
                      className="bg-yellow-500 hover:bg-yellow-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center"
                    >
                      {isPaused ? <Play className="h-5 w-5 mr-2" /> : <Pause className="h-5 w-5 mr-2" />}
                      {isPaused ? 'Resume' : 'Pause'}
                    </button>
                    <button
                      onClick={stopRecording}
                      className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center"
                    >
                      <Square className="h-5 w-5 mr-2" />
                      Stop Recording
                    </button>
                  </>
                )}
              </div>

              {/* Next Step */}
              {audioBlob && !isRecording && (
                <div className="mt-8 p-6 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center justify-center mb-4">
                    <CheckCircle className="h-6 w-6 text-green-600 mr-2" />
                    <span className="text-green-800 font-medium">Recording completed!</span>
                  </div>
                  <button
                    onClick={transcribeAudio}
                    disabled={loading}
                    className="medical-button px-6 py-3 text-white font-medium rounded-lg"
                  >
                    Process Recording
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 2: Transcript Editing */}
        {step === 'transcript' && (
          <div className="medical-card p-8 rounded-xl animate-fade-in">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-hss-primary">📝 Review & Edit Transcript</h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => copyToClipboard(editedTranscript)}
                  className="flex items-center text-gray-600 hover:text-hss-primary transition-colors"
                >
                  <Copy className="h-4 w-4 mr-1" />
                  Copy
                </button>
              </div>
            </div>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Transcript Content (editable)
                </label>
                <textarea
                  value={editedTranscript}
                  onChange={(e) => setEditedTranscript(e.target.value)}
                  className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hss-primary focus:border-transparent resize-none"
                  placeholder="Your transcript will appear here..."
                />
                <p className="text-sm text-gray-500 mt-2">
                  Review and edit the transcript before generating your professional report.
                </p>
              </div>

              <div className="flex items-center justify-between">
                <button
                  onClick={() => setStep('record')}
                  className="flex items-center text-gray-600 hover:text-hss-primary transition-colors"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Recording
                </button>
                
                <button
                  onClick={generateReport}
                  disabled={!editedTranscript.trim() || loading}
                  className="medical-button px-6 py-3 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Generate Professional Report
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Report Display */}
        {step === 'report' && (
          <div className="medical-card p-8 rounded-xl animate-fade-in">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-hss-primary">📊 Professional Report</h3>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => copyToClipboard(report)}
                  className="flex items-center text-gray-600 hover:text-hss-primary transition-colors"
                >
                  <Copy className="h-4 w-4 mr-1" />
                  Copy
                </button>
                <button
                  onClick={downloadReport}
                  className="flex items-center text-gray-600 hover:text-hss-primary transition-colors"
                >
                  <Download className="h-4 w-4 mr-1" />
                  Download
                </button>
              </div>
            </div>

            <div className="prose prose-lg max-w-none">
              <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                <ReactMarkdown>{report}</ReactMarkdown>
              </div>
            </div>

            <div className="flex items-center justify-between pt-6 border-t border-gray-200">
              <button
                onClick={() => setStep('transcript')}
                className="flex items-center text-gray-600 hover:text-hss-primary transition-colors"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Edit Transcript
              </button>
              
              <div className="flex items-center space-x-3">
                <button
                  onClick={resetProcess}
                  className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  Create New Report
                </button>
                <button
                  onClick={() => toast.success('Email functionality coming soon!')}
                  className="medical-button px-6 py-3 text-white font-medium rounded-lg flex items-center"
                >
                  <Send className="h-4 w-4 mr-2" />
                  Send via Email
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default WeeklyReportGenerator;