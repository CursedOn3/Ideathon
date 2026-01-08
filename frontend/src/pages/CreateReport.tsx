import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sparkles, Send, Loader2, FileText, LayoutTemplate, Lightbulb } from 'lucide-react';
import { AppLayout } from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';

const suggestions = [
  'Generate a Q4 marketing performance report with campaign metrics and ROI analysis',
  'Create an executive summary of our annual sales data with key insights',
  'Analyze customer satisfaction survey results and identify improvement areas',
  'Prepare a competitive market analysis for the enterprise software sector',
];

export default function CreateReport() {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const navigate = useNavigate();

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    
    setIsGenerating(true);
    // Simulate API call - would call /api/reports/generate
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsGenerating(false);
    
    // Navigate to preview with generated report
    navigate('/reports/preview', { state: { prompt } });
  };

  const handleSuggestionClick = (suggestion: string) => {
    setPrompt(suggestion);
  };

  return (
    <AppLayout>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mx-auto max-w-4xl"
      >
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
            <Sparkles className="h-4 w-4" />
            AI-Powered Generation
          </div>
          <h1 className="font-display text-3xl font-bold text-foreground">Create New Report</h1>
          <p className="mt-2 text-muted-foreground">
            Describe what you need and let AI generate a comprehensive report for you
          </p>
        </div>

        {/* Main Input Card */}
        <Card className="gradient-border mb-8 overflow-hidden">
          <CardContent className="p-0">
            <div className="relative">
              <Textarea
                placeholder="Enter your report request... (e.g., 'Generate a quarterly marketing performance analysis with campaign ROI and channel breakdowns')"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="min-h-[200px] resize-none border-0 bg-card p-6 text-lg text-foreground placeholder:text-muted-foreground focus-visible:ring-0"
              />
              
              {/* Character count */}
              <div className="absolute bottom-4 left-6 text-sm text-muted-foreground">
                {prompt.length} characters
              </div>

              {/* Generate Button */}
              <div className="absolute bottom-4 right-4">
                <Button
                  size="lg"
                  onClick={handleGenerate}
                  disabled={!prompt.trim() || isGenerating}
                  className="bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Send className="mr-2 h-4 w-4" />
                      Generate Report
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Loading State */}
        {isGenerating && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-8"
          >
            <Card className="border-border bg-card">
              <CardContent className="flex items-center gap-4 p-6">
                <div className="relative">
                  <div className="h-12 w-12 rounded-full bg-primary/20" />
                  <motion.div
                    className="absolute inset-0 rounded-full border-2 border-primary border-t-transparent"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  />
                </div>
                <div>
                  <p className="font-medium text-foreground">Analyzing your request...</p>
                  <p className="text-sm text-muted-foreground">
                    Gathering data, generating insights, and structuring your report
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Suggestions */}
        <div className="mb-8">
          <div className="mb-4 flex items-center gap-2 text-sm font-medium text-muted-foreground">
            <Lightbulb className="h-4 w-4" />
            Suggestions
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {suggestions.map((suggestion, index) => (
              <motion.button
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                onClick={() => handleSuggestionClick(suggestion)}
                className="group rounded-lg border border-border bg-card p-4 text-left transition-all hover:border-primary/30 hover:bg-secondary/50"
              >
                <p className="text-sm text-foreground group-hover:text-primary transition-colors">
                  {suggestion}
                </p>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid gap-4 sm:grid-cols-2">
          <Card className="glass-hover border-border bg-card">
            <CardContent className="flex items-center gap-4 p-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <LayoutTemplate className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="font-medium text-foreground">Use a Template</p>
                <p className="text-sm text-muted-foreground">Start with a pre-built format</p>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-hover border-border bg-card">
            <CardContent className="flex items-center gap-4 p-6">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-accent/10">
                <FileText className="h-6 w-6 text-accent" />
              </div>
              <div>
                <p className="font-medium text-foreground">Upload Data</p>
                <p className="text-sm text-muted-foreground">Import spreadsheets or files</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </motion.div>
    </AppLayout>
  );
}
