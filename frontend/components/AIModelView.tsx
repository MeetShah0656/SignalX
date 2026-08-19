'use client';

import React, { useState } from 'react';
import { BrainCircuit, Cpu, CheckCircle2, Play, AlertCircle, BarChart2 } from 'lucide-react';

interface AIModelViewProps {
  modelStatus: any;
  onTrainModel: (params: any) => Promise<any>;
}

export const AIModelView: React.FC<AIModelViewProps> = ({ modelStatus, onTrainModel }) => {
  const [isTraining, setIsTraining] = useState(false);
  const [trainingStep, setTrainingStep] = useState<string | null>(null);
  const [trainingResult, setTrainingResult] = useState<any>(null);

  const handleTrainClick = async () => {
    setIsTraining(true);
    const steps = [
      "Loading historical candle datasets...",
      "Generating technical feature matrix...",
      "Chronologically splitting train / validation sets...",
      "Training XGBoost, RandomForest & LogisticRegression...",
      "Evaluating out-of-sample test set metrics...",
      "Saving best model to local model registry..."
    ];

    for (const step of steps) {
      setTrainingStep(step);
      await new Promise((r) => setTimeout(r, 400));
    }

    try {
      const res = await onTrainModel({ limit: 500, timeframe: '5m' });
      setTrainingResult(res);
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsTraining(false);
      setTrainingStep(null);
    }
  };

  const activeModel = trainingResult?.result?.result || modelStatus?.active_model;
  const metrics = activeModel?.metrics || {};

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <BrainCircuit className="w-5 h-5 text-purple-400" />
            <span>Machine Learning Model Management</span>
          </h2>
          <p className="text-xs text-textMuted mt-1">Train, evaluate, and inspect quantitative machine learning models.</p>
        </div>

        <button
          onClick={handleTrainClick}
          disabled={isTraining}
          className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-purple-500/20 flex items-center space-x-2 transition-all"
        >
          <Cpu className="w-4 h-4" />
          <span>{isTraining ? 'TRAINING IN PROGRESS...' : 'START MODEL TRAINING PIPELINE'}</span>
        </button>
      </div>

      {/* Progress Box */}
      {trainingStep && (
        <div className="p-4 bg-purple-950/40 border border-purple-800/40 rounded-xl text-xs font-mono text-purple-200 flex items-center space-x-3 animate-pulse">
          <Cpu className="w-5 h-5 text-purple-400 shrink-0" />
          <div>
            <div className="font-bold">Training Pipeline Executing...</div>
            <div className="text-textMuted mt-0.5">{trainingStep}</div>
          </div>
        </div>
      )}

      {/* Active Model Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 font-mono">
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-textMuted font-sans uppercase">Active Model Version</div>
          <div className="text-xl font-black text-purple-400 mt-1">{activeModel?.model_version || 'NOT TRAINED'}</div>
          <div className="text-[11px] text-textMuted font-sans mt-1">Type: {activeModel?.model_type || 'XGBOOST'}</div>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-textMuted font-sans uppercase">Test Accuracy</div>
          <div className="text-3xl font-black text-white mt-1">
            {metrics.accuracy ? `${(metrics.accuracy * 100).toFixed(1)}%` : 'N/A'}
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-textMuted font-sans uppercase">Macro F1 Score</div>
          <div className="text-3xl font-black text-emerald-400 mt-1">
            {metrics.f1_score ? metrics.f1_score.toFixed(4) : 'N/A'}
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-textMuted font-sans uppercase">Training Samples</div>
          <div className="text-3xl font-black text-blue-400 mt-1">{metrics.train_samples || 0}</div>
          <div className="text-[11px] text-textMuted font-sans mt-1">Test Samples: {metrics.test_samples || 0}</div>
        </div>
      </div>

      {/* Feature Importance Table */}
      {metrics.feature_importance && (
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="font-bold text-white text-sm mb-4 flex items-center space-x-2">
            <BarChart2 className="w-4 h-4 text-purple-400" />
            <span>XGBoost Feature Importance Breakdown</span>
          </h3>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 font-mono text-xs">
            {Object.entries(metrics.feature_importance).map(([feat, score]: [string, any]) => (
              <div key={feat} className="bg-surface border border-border p-3 rounded-lg flex items-center justify-between">
                <span className="text-textMuted font-sans">{feat}</span>
                <span className="font-bold text-purple-400">{score.toFixed(4)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
