"""
AI agent service for email generation.

This module handles integration with OpenAI API for generating personalized
email content based on client data and follow-up context.
"""

import json
import logging
from typing import Dict, Optional
from app.models.client import Client
from app.models.task import Task
from app.config import settings
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

logger = logging.getLogger(__name__)

class AIAgent:
    """Service for AI-powered email generation using OpenAI."""
    
    def __init__(self):
        """Initialize AI agent with OpenAI configuration."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
    
    def _build_prompt(
        self, 
        client: Client, 
        task: Task, 
        agent_instructions: Optional[str] = None
    ) -> str:
        """
        Build a detailed prompt for OpenAI that generates personalized real estate follow-up emails.
        
        Args:
            client: Client model with name, email, property_address, property_type, stage, notes, custom_fields
            task: Task model with followup_type, scheduled_for, priority, notes
            agent_instructions: Optional custom instructions from user
            
        Returns:
            String containing the full prompt for OpenAI
        """
        # System message
        prompt_parts = [
            "You are a professional real estate agent assistant.",
            "Your task is to write personalized, professional follow-up emails.",
            "Tone: Friendly, professional, helpful (not pushy).",
            "Goal: Build relationship, provide value, move deal forward.",
            "",
            "=== CLIENT INFORMATION ===",
            f"Name: {client.name}",
            f"Email: {client.email}",
            f"Property Type: {client.property_type}",
            f"Property Address: {client.property_address or 'Not specified'}",
            f"Current Stage: {client.stage}",
        ]
        
        # Add client notes if available
        if client.notes:
            prompt_parts.append(f"Notes: {client.notes}")
        
        # Add custom fields if available and relevant
        if client.custom_fields:
            custom_info = []
            for key, value in client.custom_fields.items():
                custom_info.append(f"{key}: {value}")
            if custom_info:
                prompt_parts.append(f"Additional Information: {', '.join(custom_info)}")
        
        prompt_parts.append("")
        prompt_parts.append("=== FOLLOW-UP TYPE ===")
        
        # Context based on follow-up type
        followup_context = {
            "Day 1": (
                "Initial contact after client expressed interest.",
                "Goals:\n"
                "- Introduce yourself warmly\n"
                "- Confirm their interest\n"
                "- Offer to answer questions\n"
                "- Suggest next steps (phone call or showing)"
            ),
            "Day 3": (
                "Second follow-up to maintain engagement.",
                "Goals:\n"
                "- Check in on their thoughts\n"
                "- Answer any questions they may have\n"
                "- Offer additional information or resources\n"
                "- Maintain momentum"
            ),
            "Week 1": (
                "Weekly check-in to provide updates.",
                "Goals:\n"
                "- Provide market insights or updates\n"
                "- Schedule a property showing if not done\n"
                "- Share relevant listings if appropriate\n"
                "- Show continued interest and availability"
            ),
            "Week 2": (
                "Bi-weekly follow-up for nurturing.",
                "Goals:\n"
                "- Follow up on any showings or interactions\n"
                "- Address any concerns or questions\n"
                "- Provide additional value or information\n"
                "- Move the conversation forward"
            ),
            "Month 1": (
                "Monthly follow-up for long-term nurturing.",
                "Goals:\n"
                "- Long-term relationship building\n"
                "- Share new listings that might interest them\n"
                "- Provide market updates or insights\n"
                "- Stay top-of-mind without being pushy"
            )
        }
        
        followup_type = task.followup_type
        if followup_type in followup_context:
            context, goals = followup_context[followup_type]
            prompt_parts.append(f"{followup_type} Follow-up")
            prompt_parts.append(context)
            prompt_parts.append(goals)
        else:
            prompt_parts.append(f"{followup_type} Follow-up")
            prompt_parts.append("General follow-up to maintain engagement and provide value.")
        
        # Add task priority and notes if available
        if task.priority:
            prompt_parts.append(f"Priority: {task.priority}")
        if task.notes:
            prompt_parts.append(f"Task Notes: {task.notes}")
        
        prompt_parts.append("")
        prompt_parts.append("=== INSTRUCTIONS ===")
        
        # Add custom agent instructions if provided
        if agent_instructions:
            prompt_parts.append(f"Custom Instructions: {agent_instructions}")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "- Write a friendly, professional email",
            "- Keep it concise (3-5 short paragraphs)",
            "- Use the client's name naturally",
            "- Reference the specific property when relevant",
            "- Include a clear call-to-action",
            "- End with a professional closing",
            "",
            "=== OUTPUT FORMAT ===",
            "Return a JSON object with the following structure:",
            '{',
            '  "subject": "Brief subject line (5-10 words)",',
            '  "body": "Full email body with paragraphs separated by \\n\\n"',
            '}',
            "",
            "Write the email now."
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_openai_response(self, response: ChatCompletion) -> Dict[str, str]:
        """
        Extract subject and body from OpenAI API response.
        
        Args:
            response: OpenAI ChatCompletion response object
            
        Returns:
            Dictionary with subject, body, and preview keys
        """
        try:
            if not response or not response.choices:
                logger.error("OpenAI response is empty or missing choices")
                return self._get_fallback_email(None, None)
            
            content = response.choices[0].message.content
            if not content:
                logger.error("OpenAI response content is empty")
                return self._get_fallback_email(None, None)
            
            # Try JSON parsing first
            try:
                # Clean content - remove markdown code blocks if present
                content_clean = content.strip()
                if content_clean.startswith("```json"):
                    content_clean = content_clean.replace("```json", "").replace("```", "").strip()
                elif content_clean.startswith("```"):
                    content_clean = content_clean.replace("```", "").strip()
                
                data = json.loads(content_clean)
                subject = data.get("subject", "").strip()
                body = data.get("body", "").strip()
                
                # Validate that we got both subject and body
                if not subject or not body:
                    logger.warning("JSON parsed but missing subject or body, falling back to text parsing")
                    raise ValueError("Missing required fields")
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.warning(f"JSON parsing failed: {e}, attempting text parsing")
                
                # Fallback to text parsing
                lines = content.split("\n")
                subject = ""
                body_parts = []
                found_subject = False
                
                for line in lines:
                    line_lower = line.lower()
                    if not found_subject and ("subject:" in line_lower or "subject :" in line_lower):
                        subject = line.split(":", 1)[-1].strip()
                        found_subject = True
                    elif not found_subject and len(line.strip()) > 0 and len(line.strip()) < 100:
                        # First non-empty short line might be subject
                        subject = line.strip()
                        found_subject = True
                    else:
                        body_parts.append(line)
                
                body = "\n".join(body_parts).strip()
                
                # If we still don't have a subject, use first line
                if not subject and body:
                    first_line = body.split("\n")[0]
                    subject = first_line[:80].strip()
                    body = "\n".join(body.split("\n")[1:]).strip()
                
                # If still no subject, use default
                if not subject:
                    subject = "Following up on your property inquiry"
            
            # Validate final output
            if not subject:
                subject = "Following up on your property inquiry"
            if not body:
                logger.error("Failed to extract email body from OpenAI response")
                return self._get_fallback_email(None, None)
            
            # Generate preview (first 150-200 characters)
            preview = body[:200] if len(body) > 200 else body
            if len(body) > 200:
                # Try to cut at word boundary
                last_space = preview.rfind(" ")
                if last_space > 150:
                    preview = preview[:last_space] + "..."
                else:
                    preview = preview + "..."
            
            return {
                "subject": subject,
                "body": body,
                "preview": preview
            }
            
        except Exception as e:
            logger.error(f"Error parsing OpenAI response: {e}", exc_info=True)
            return self._get_fallback_email(None, None)
    
    async def generate_email(
        self,
        client: Client,
        task: Task,
        agent_instructions: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate personalized email content for a client and task using OpenAI.
        
        Args:
            client: Client model instance
            task: Task model instance
            agent_instructions: Optional custom instructions for the agent
            
        Returns:
            Dictionary with 'subject', 'body', and 'preview' keys
        """
        logger.info(f"Generating email for client_id={client.id}, task_id={task.id}, followup_type={task.followup_type}")
        
        try:
            # Build the prompt
            prompt = self._build_prompt(client, task, agent_instructions)
            
            # Call OpenAI API
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional real estate agent assistant. "
                                     "You write personalized, professional follow-up emails that build relationships "
                                     "and provide value to clients. Your tone is friendly, professional, and helpful, "
                                     "never pushy or salesy."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=self.max_tokens,
                    temperature=0.7,  # Creative but focused
                    response_format={"type": "json_object"}  # Request JSON format for better parsing
                )
                
                # Parse the response
                result = self._parse_openai_response(response)
                
                logger.info(f"Successfully generated email for client_id={client.id}, task_id={task.id}")
                return result
                
            except Exception as api_error:
                error_msg = str(api_error)
                logger.error(
                    f"OpenAI API error for client_id={client.id}, task_id={task.id}: {error_msg}",
                    exc_info=True
                )
                
                # Handle specific error types
                if "rate_limit" in error_msg.lower() or "429" in error_msg:
                    logger.warning("OpenAI rate limit encountered. Consider implementing retry logic.")
                elif "authentication" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
                    logger.error("OpenAI authentication error. Check OPENAI_API_KEY configuration.")
                
                # Return fallback email
                return self._get_fallback_email(client, task)
                
        except Exception as e:
            logger.error(
                f"Unexpected error generating email for client_id={client.id}, task_id={task.id}: {e}",
                exc_info=True
            )
            return self._get_fallback_email(client, task)
    
    async def generate_email_preview(
        self,
        client: Client,
        task: Task,
        agent_instructions: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate email preview without actually sending (optimized for faster response).
        
        This method is similar to generate_email but may use reduced tokens for faster preview generation.
        
        Args:
            client: Client model instance
            task: Task model instance
            agent_instructions: Optional custom instructions for the agent
            
        Returns:
            Dictionary with 'subject', 'body', and 'preview' keys
        """
        logger.info(f"Generating email preview for client_id={client.id}, task_id={task.id}")
        
        try:
            # Build the prompt
            prompt = self._build_prompt(client, task, agent_instructions)
            
            # Call OpenAI API with slightly reduced tokens for faster preview
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional real estate agent assistant. "
                                     "You write personalized, professional follow-up emails that build relationships "
                                     "and provide value to clients. Your tone is friendly, professional, and helpful, "
                                     "never pushy or salesy."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=min(300, self.max_tokens),  # Reduced for faster preview
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                
                # Parse the response
                result = self._parse_openai_response(response)
                
                logger.info(f"Successfully generated email preview for client_id={client.id}, task_id={task.id}")
                return result
                
            except Exception as api_error:
                error_msg = str(api_error)
                logger.error(
                    f"OpenAI API error generating preview for client_id={client.id}, task_id={task.id}: {error_msg}",
                    exc_info=True
                )
                return self._get_fallback_email(client, task)
                
        except Exception as e:
            logger.error(
                f"Unexpected error generating preview for client_id={client.id}, task_id={task.id}: {e}",
                exc_info=True
            )
            return self._get_fallback_email(client, task)
    
    def _get_fallback_email(self, client: Optional[Client], task: Optional[Task]) -> Dict[str, str]:
        """
        Return a simple fallback email if AI generation fails.
        
        Args:
            client: Client model instance (can be None)
            task: Task model instance (can be None)
            
        Returns:
            Dictionary with subject, body, and preview keys
        """
        if client:
            client_name = client.name
            property_address = client.property_address or "your inquiry"
            
            subject = f"Following up on {property_address}"
            body = f"""Hi {client_name},

I wanted to follow up with you regarding {property_address}.

I'd love to help answer any questions you might have and discuss next steps.

Would you be available for a quick call this week? I'm happy to schedule a time that works for you.

Best regards,
Your Real Estate Agent"""
        else:
            subject = "Following up on your inquiry"
            body = """Hi,

I wanted to follow up with you regarding your recent inquiry.

I'd love to help answer any questions you might have and discuss next steps.

Would you be available for a quick call this week?

Best regards,
Your Real Estate Agent"""
        
        preview = body[:200] + "..." if len(body) > 200 else body
        
        logger.info("Using fallback email template")
        return {
            "subject": subject,
            "body": body,
            "preview": preview
        }
