'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { usePreviewEmail } from '@/lib/hooks/mutations/usePreviewEmail';
import { useSendEmail } from '@/lib/hooks/mutations/useSendEmail';
import { useUpdateTask } from '@/lib/hooks/mutations/useUpdateTask';
import { useTask } from '@/lib/hooks/queries/useTasks';
import { useToast } from '@/lib/hooks/ui/useToast';
import { useQueryClient } from '@tanstack/react-query';
import { tasksApi } from '@/lib/api/endpoints/tasks';
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
import { AlertCircle, Loader2, RefreshCw, Send, Save } from 'lucide-react';
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

// Fallback to localStorage if database is not available
const getPreviewStorageKey = (taskId: number) => `email_preview_${taskId}`;

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
  const queryClient = useQueryClient();
  const previewEmail = usePreviewEmail();
  const sendEmail = useSendEmail();
  const updateTask = useUpdateTask();
  const { data: task } = useTask(taskId, { enabled: open });

  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [customInstructions, setCustomInstructions] = useState('');
  const [isEditMode, setIsEditMode] = useState(false);
  const [hasGenerated, setHasGenerated] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  
  // Use ref to track if we've already attempted to generate to prevent duplicate calls
  const hasAttemptedGenerate = useRef(false);
  const isGeneratingRef = useRef(false);
  const isSavingRef = useRef(false); // Track when we're saving to prevent regeneration
  const saveQueueRef = useRef<Promise<any> | null>(null); // Queue saves to prevent conflicts
  const pendingSaveTimeoutRef = useRef<NodeJS.Timeout | null>(null); // Track pending auto-save

  // Save preview to database with queue to prevent conflicts
  const savePreviewToDatabase = useCallback(async (preview: { subject: string; body: string; custom_instructions?: string }, skipInvalidation = false) => {
    // Queue saves to prevent concurrent conflicts
    if (saveQueueRef.current) {
      // Wait for previous save to complete
      await saveQueueRef.current;
    }
    
    // Create new save promise
    const savePromise = (async () => {
      try {
        setIsSaving(true);
        isSavingRef.current = true; // Mark that we're saving
        const previewData = {
          ...preview,
          timestamp: Date.now()
        };
        
        // Call API directly to avoid automatic invalidation from useUpdateTask hook
        const result = await tasksApi.update(taskId, {
          email_preview: previewData
        });
        
        // Always update cache first
        queryClient.setQueryData(['task', taskId], (oldData: any) => {
          if (oldData) {
            return { ...oldData, email_preview: previewData };
          }
          return oldData;
        });
        
        // Always invalidate to ensure UI consistency, but use a flag to prevent regeneration loop
        if (!skipInvalidation) {
          // For manual saves, invalidate immediately
          await queryClient.invalidateQueries({ queryKey: ['task', taskId] });
        } else {
          // For auto-saves, invalidate after a delay to prevent regeneration during save
          setTimeout(() => {
            queryClient.invalidateQueries({ queryKey: ['task', taskId] });
          }, 2000);
        }
        
        // Also save to localStorage as backup
        const storageKey = getPreviewStorageKey(taskId);
        localStorage.setItem(storageKey, JSON.stringify(previewData));
        
        console.log('Preview saved to database successfully', result);
        return result;
      } catch (error: any) {
        console.error('Failed to save preview to database:', error);
        const errorMessage = error.response?.data?.detail || 
                            error.response?.data?.message ||
                            error.message ||
                            "Failed to save preview";
        
        // Always fallback to localStorage, even if error handling fails
        try {
          const storageKey = getPreviewStorageKey(taskId);
          const previewData = {
            ...preview,
            timestamp: Date.now()
          };
          localStorage.setItem(storageKey, JSON.stringify(previewData));
          console.log('Preview saved to localStorage as fallback');
        } catch (localStorageError) {
          console.error('Failed to save to localStorage:', localStorageError);
        }
        
        // Show error toast but don't block the user
        toast({
          title: "Warning: Preview not saved",
          description: "Preview saved locally. " + errorMessage,
          variant: "default",
        });
        
        throw error; // Re-throw to allow caller to handle if needed
      } finally {
        setIsSaving(false);
        // Reset saving flag immediately after save completes
        isSavingRef.current = false;
      }
    })();
    
    // Store promise in queue
    saveQueueRef.current = savePromise;
    
    // Clear queue after completion
    savePromise.finally(() => {
      if (saveQueueRef.current === savePromise) {
        saveQueueRef.current = null;
      }
    });
    
    return savePromise;
  }, [taskId, queryClient, toast]);

  const handleGenerate = async () => {
    // Prevent duplicate calls
    if (isGeneratingRef.current) {
      return;
    }
    
    try {
      isGeneratingRef.current = true;
      setHasGenerated(true);
      const preview = await previewEmail.mutateAsync({
        client_id: clientId,
        task_id: taskId,
        agent_instructions: customInstructions || undefined
      });

      setSubject(preview.subject);
      setBody(preview.body);
      setIsEditMode(false);
      // Save to database after generation, but skip invalidation to avoid triggering useEffect
      try {
        await savePreviewToDatabase({
          subject: preview.subject,
          body: preview.body,
          custom_instructions: customInstructions || undefined
        }, true); // skipInvalidation = true
      } catch (saveError) {
        // Error already handled in savePreviewToDatabase, just log
        console.warn('Preview generation succeeded but save failed:', saveError);
      }
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
    } finally {
      isGeneratingRef.current = false;
    }
  };

  // Load stored preview on open (from database or localStorage)
  useEffect(() => {
    if (!open) {
      // Execute any pending auto-save before closing
      if (pendingSaveTimeoutRef.current) {
        clearTimeout(pendingSaveTimeoutRef.current);
        // Execute the pending save immediately
        if (hasGenerated && subject && body && !isGeneratingRef.current) {
          savePreviewToDatabase({
            subject,
            body,
            custom_instructions: customInstructions || undefined
          }, true).catch(err => {
            console.error('Failed to save pending preview before close:', err);
          });
        }
        pendingSaveTimeoutRef.current = null;
      }
      
      // Reset flags when modal closes
      hasAttemptedGenerate.current = false;
      isGeneratingRef.current = false;
      // Don't reset isSavingRef here - let it complete naturally
      return;
    }
    
    // Don't regenerate if we already have content loaded (unless modal was just opened)
    if (hasGenerated && subject && body && hasAttemptedGenerate.current) {
      console.log('Skipping preview load - already have content loaded');
      return;
    }
    
    // Reset flag when modal opens to allow loading (only if we don't have content)
    if (!hasGenerated) {
      hasAttemptedGenerate.current = false;
    }
    
    // Wait for task to load before attempting to load preview
    const loadPreview = async () => {
      // Wait for any ongoing save to complete (but don't block forever)
      if (isSavingRef.current && saveQueueRef.current) {
        try {
          await Promise.race([
            saveQueueRef.current,
            new Promise(resolve => setTimeout(resolve, 2000)) // Max wait 2s
          ]);
        } catch (e) {
          console.warn('Save queue wait failed:', e);
        }
      }
      
      // Prevent duplicate generation attempts
      if (hasAttemptedGenerate.current && hasGenerated) {
        return;
      }
      
      // Mark that we've attempted to load/generate
      hasAttemptedGenerate.current = true;
      
      let loadedPreview = false;
      
      // First, try to load from database if task is loaded
      if (task?.email_preview) {
        const preview = task.email_preview;
        // If preview exists and has subject/body, use it (regardless of age if manually saved)
        if (preview.subject && preview.body) {
          // Only update if content is different (to avoid unnecessary updates)
          if (preview.subject !== subject || preview.body !== body) {
            setSubject(preview.subject);
            setBody(preview.body);
            setCustomInstructions(preview.custom_instructions || '');
            setHasGenerated(true);
            setIsEditMode(false);
            loadedPreview = true;
            console.log('Loaded preview from database:', preview);
          } else {
            // Content matches, just mark as loaded
            loadedPreview = true;
            console.log('Preview already matches database content');
          }
        }
      }
      
      // Fallback to localStorage if no database preview
      if (!loadedPreview) {
        const storageKey = getPreviewStorageKey(taskId);
        const stored = localStorage.getItem(storageKey);
        
        if (stored) {
          try {
            const preview = JSON.parse(stored);
            const age = Date.now() - (preview.timestamp || 0);
            const maxAge = 24 * 60 * 60 * 1000; // 24 hours
            
            if (age < maxAge && preview.subject && preview.body) {
              setSubject(preview.subject);
              setBody(preview.body);
              setCustomInstructions(preview.customInstructions || preview.custom_instructions || '');
              setHasGenerated(true);
              setIsEditMode(false);
              loadedPreview = true;
              console.log('Loaded preview from localStorage:', preview);
            } else {
              localStorage.removeItem(storageKey);
            }
          } catch (e) {
            console.error('Failed to parse stored preview:', e);
            localStorage.removeItem(storageKey);
          }
        }
      }
      
      // If no stored preview and we don't have content, generate new one (only if not already generating)
      if (!loadedPreview && !hasGenerated && !isGeneratingRef.current) {
        console.log('No saved preview found, generating new email');
        handleGenerate();
      }
    };
    
    // Wait for task to be loaded before checking for preview
    if (task) {
      // Task is loaded, check for preview
      loadPreview();
    } else {
      // Task not loaded yet, wait a bit longer and try again
      // The effect will re-run when task becomes available
      const timeoutId = setTimeout(() => {
        // If task still not loaded after timeout, try loading anyway (might use localStorage)
        console.log('Task not loaded yet, attempting to load preview anyway');
        loadPreview();
      }, 500); // Increased timeout to 500ms to give task time to load
      return () => clearTimeout(timeoutId);
    }
    // Depend on task object to re-run when task data changes (e.g., after save)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, taskId, task]);

  // Save preview to database whenever it changes (debounced)
  // Only save if user manually edited (not during initial generation)
  useEffect(() => {
    if (hasGenerated && subject && body && !isGeneratingRef.current) {
      // Clear any pending save
      if (pendingSaveTimeoutRef.current) {
        clearTimeout(pendingSaveTimeoutRef.current);
      }
      
      // Debounce saves to avoid too many API calls
      pendingSaveTimeoutRef.current = setTimeout(() => {
        savePreviewToDatabase({
          subject,
          body,
          custom_instructions: customInstructions || undefined
        }, true).catch(err => {
          console.error('Auto-save failed:', err);
        });
        pendingSaveTimeoutRef.current = null;
      }, 1000); // Wait 1 second after last change
      
      return () => {
        if (pendingSaveTimeoutRef.current) {
          clearTimeout(pendingSaveTimeoutRef.current);
          pendingSaveTimeoutRef.current = null;
        }
      };
    }
  }, [subject, body, customInstructions, hasGenerated, taskId, savePreviewToDatabase]);

  const handleRegenerate = async () => {
    // Clear stored preview when regenerating
    const storageKey = getPreviewStorageKey(taskId);
    localStorage.removeItem(storageKey);
    // Clear from database
    try {
      await updateTask.mutateAsync({
        id: taskId,
        data: { email_preview: null as any as any }
      });
      // Don't invalidate here to avoid triggering useEffect
    } catch (error) {
      console.error('Failed to clear preview from database:', error);
    }
    setHasGenerated(false);
    hasAttemptedGenerate.current = false; // Reset flag to allow regeneration
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

      // Clear stored preview after sending (from both database and localStorage)
      const storageKey = getPreviewStorageKey(taskId);
      localStorage.removeItem(storageKey);
      // Clear from database
      try {
        await updateTask.mutateAsync({
          id: taskId,
          data: { email_preview: null as any }
        });
        queryClient.invalidateQueries({ queryKey: ['task', taskId] });
      } catch (error) {
        console.error('Failed to clear preview from database:', error);
      }

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

  const handleSave = async () => {
    if (!subject || !body) {
      toast({
        title: "Cannot save",
        description: "Subject and body are required",
        variant: "destructive",
      });
      return;
    }

    try {
      // Save to database (this will update cache and invalidate query)
      await savePreviewToDatabase({
        subject,
        body,
        custom_instructions: customInstructions || undefined
      }, false); // Don't skip invalidation for manual save
      
      toast({
        title: "Preview saved!",
        description: "Your changes have been saved to the database.",
      });
    } catch (error: any) {
      // Error already handled in savePreviewToDatabase
      console.error('Failed to save preview:', error);
    }
  };

  const handleClose = () => {
    setSubject('');
    setBody('');
    setCustomInstructions('');
    setHasGenerated(false);
    setIsEditMode(false);
    hasAttemptedGenerate.current = false; // Reset flag when closing
    isGeneratingRef.current = false;
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            Email Preview
            {isSaving && (
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
            )}
          </DialogTitle>
          <DialogDescription>
            AI-generated email for {clientName}
            {isSaving && <span className="ml-2 text-xs">(Saving...)</span>}
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
                    onClick={() => {
                      setIsEditMode(!isEditMode);
                    }}
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
            {hasGenerated && (
              <Button
                variant="outline"
                onClick={handleSave}
                disabled={isSaving || !subject || !body}
              >
                {isSaving ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save
                  </>
                )}
              </Button>
            )}
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

