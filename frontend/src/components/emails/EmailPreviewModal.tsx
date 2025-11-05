'use client';

import { useState, useEffect } from 'react';
import { usePreviewEmail } from '@/lib/hooks/mutations/usePreviewEmail';
import { useSendEmail } from '@/lib/hooks/mutations/useSendEmail';
import { useToast } from '@/lib/hooks/ui/useToast';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import { EmailComposer } from '@/components/emails/EmailComposer';
import { CustomInstructionsInput } from '@/components/emails/CustomInstructionsInput';
import { AlertCircle, Loader2, RefreshCw, Send } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useRouter } from 'next/navigation';

interface EmailPreviewModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  clientId: number;
  clientEmail: string;
  clientName: string;
  taskId: number;
}

export function EmailPreviewModal({
  open,
  onOpenChange,
  clientId,
  clientEmail,
  clientName,
  taskId
}: EmailPreviewModalProps) {
  const router = useRouter();
  const { toast } = useToast();
  const previewEmail = usePreviewEmail();
  const sendEmail = useSendEmail();

  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [customInstructions, setCustomInstructions] = useState('');
  const [isEditMode, setIsEditMode] = useState(false);
  const [hasGenerated, setHasGenerated] = useState(false);

  // Generate preview on open
  useEffect(() => {
    if (open && !hasGenerated) {
      handleGenerate();
    }
  }, [open]);

  const handleGenerate = async () => {
    try {
      setHasGenerated(true);
      const preview = await previewEmail.mutateAsync({
        client_id: clientId,
        task_id: taskId,
        agent_instructions: customInstructions || undefined
      });

      setSubject(preview.subject);
      setBody(preview.body);
      setIsEditMode(false);
    } catch (error: any) {
      console.error('Email preview error:', error);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message ||
                          error.message ||
                          "AI service may be unavailable. Please try again.";
      toast({
        title: "Error generating email",
        description: errorMessage,
        variant: "destructive",
      });
      // Set fallback template on error
      setSubject(`Follow-up: ${clientName}`);
      setBody(`<p>Hi ${clientName},</p><p>I wanted to follow up with you regarding your property search. Please let me know if you have any questions or would like to schedule a viewing.</p><p>Best regards</p>`);
    }
  };

  const handleRegenerate = () => {
    setHasGenerated(false);
    handleGenerate();
  };

  const handleSend = async () => {
    try {
      const sentEmail = await sendEmail.mutateAsync({
        client_id: clientId,
        task_id: taskId,
        to_email: clientEmail,
        subject,
        body,
        agent_instructions: customInstructions || undefined
      });

      toast({
        title: "Email sent!",
        description: `Email successfully sent to ${clientEmail}`,
      });

      onOpenChange(false);
      router.push(`/emails/${sentEmail.id}`);
    } catch (error: any) {
      toast({
        title: "Error sending email",
        description: error.response?.data?.detail || "Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleClose = () => {
    setSubject('');
    setBody('');
    setCustomInstructions('');
    setHasGenerated(false);
    setIsEditMode(false);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Email Preview</DialogTitle>
          <DialogDescription>
            AI-generated email for {clientName}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Loading State */}
          {previewEmail.isPending && !hasGenerated && (
            <div className="space-y-4">
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
                  <p className="text-lg font-medium">Generating personalized email...</p>
                  <p className="text-sm text-muted-foreground">
                    This may take a few seconds
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Error State */}
          {previewEmail.isError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <div className="ml-2">
                <AlertDescription>
                  Failed to generate email. Using fallback template. You can edit it below.
                </AlertDescription>
              </div>
            </Alert>
          )}

          {/* Preview/Edit State */}
          {hasGenerated && !previewEmail.isPending && (
            <>
              {/* To Field (Read-only) */}
              <div className="space-y-2">
                <Label>To</Label>
                <Input value={clientEmail} disabled />
              </div>

              {/* Subject Field */}
              <div className="space-y-2">
                <Label htmlFor="subject">Subject</Label>
                <Input
                  id="subject"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="Email subject"
                />
              </div>

              {/* Body Field */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <Label>Email Body</Label>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsEditMode(!isEditMode)}
                  >
                    {isEditMode ? 'Preview' : 'Edit'}
                  </Button>
                </div>
                <EmailComposer
                  value={body}
                  onChange={setBody}
                  readOnly={!isEditMode}
                />
              </div>

              {/* Custom Instructions (Collapsible) */}
              <CustomInstructionsInput
                value={customInstructions}
                onChange={setCustomInstructions}
              />
            </>
          )}
        </div>

        <DialogFooter className="flex justify-between">
          <div className="flex gap-2">
            {hasGenerated && (
              <Button
                variant="outline"
                onClick={handleRegenerate}
                disabled={previewEmail.isPending}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${previewEmail.isPending ? 'animate-spin' : ''}`} />
                Regenerate
              </Button>
            )}
          </div>

          <div className="flex gap-2">
            <Button variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button
              onClick={handleSend}
              disabled={!hasGenerated || sendEmail.isPending || !subject || !body}
            >
              {sendEmail.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Send Email
                </>
              )}
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

