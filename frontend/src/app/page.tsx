'use client';

import { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import {
  Users,
  Sparkles,
  Calendar,
  BarChart3,
  ArrowRight,
  Brain,
  Clock,
  RefreshCw,
  Network,
  ChevronDown,
  CheckCircle2,
} from 'lucide-react';
import { ROUTES } from '@/lib/constants/routes';

// Animated Counter Component
function AnimatedCounter({ end, duration = 2000, suffix = '' }: { end: number; duration?: number; suffix?: string }) {
  const [count, setCount] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isVisible) {
          setIsVisible(true);
        }
      },
      { threshold: 0.5 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [isVisible]);

  useEffect(() => {
    if (!isVisible) return;

    let startTime: number | null = null;
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      setCount(Math.floor(easeOutQuart * end));

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setCount(end);
      }
    };

    requestAnimationFrame(animate);
  }, [isVisible, end, duration]);

  return <span ref={ref}>{count}{suffix}</span>;
}

// Scroll Animation Wrapper
function ScrollAnimation({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      className={`transition-all duration-1000 ease-out ${
        isVisible
          ? 'opacity-100 translate-y-0'
          : 'opacity-0 translate-y-10'
      }`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  );
}

export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false);
  const [activeSection, setActiveSection] = useState('home');
  const [scrollProgress, setScrollProgress] = useState(0);
  const [bubbles, setBubbles] = useState<Array<{
    left: string;
    top: string;
    width: string;
    height: string;
    animationDelay: string;
    animationDuration: string;
  }>>([]);

  // Generate bubbles only on client side to avoid hydration mismatch
  useEffect(() => {
    setBubbles(
      Array.from({ length: 15 }, () => ({
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        width: `${20 + Math.random() * 60}px`,
        height: `${20 + Math.random() * 60}px`,
        animationDelay: `${Math.random() * 5}s`,
        animationDuration: `${4 + Math.random() * 4}s`,
      }))
    );
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);

      // Calculate scroll progress
      const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
      const scrolled = window.scrollY;
      const progress = scrollHeight > 0 ? (scrolled / scrollHeight) * 100 : 0;
      setScrollProgress(Math.min(progress, 100));

      // Update active section based on scroll position
      const sections = ['home', 'features', 'how-it-works', 'results', 'cta'];
      const scrollPosition = window.scrollY + 100;

      for (const section of sections) {
        const element = document.getElementById(section);
        if (element) {
          const { offsetTop, offsetHeight } = element;
          if (scrollPosition >= offsetTop && scrollPosition < offsetTop + offsetHeight) {
            setActiveSection(section);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Initial call
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation Header */}
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled
            ? 'bg-white/95 backdrop-blur-md shadow-sm border-b'
            : 'bg-transparent'
        }`}
      >
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <Link href="/" className="text-xl font-bold flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">R</span>
              </div>
              <span className="text-foreground">RealtorOS</span>
            </Link>
            <nav className="hidden md:flex items-center gap-8">
              <button
                onClick={() => scrollToSection('home')}
                className={`text-sm font-medium transition-colors hover:text-primary ${
                  activeSection === 'home' ? 'text-primary' : 'text-muted-foreground'
                }`}
              >
                Home
              </button>
              <button
                onClick={() => scrollToSection('features')}
                className={`text-sm font-medium transition-colors hover:text-primary ${
                  activeSection === 'features' ? 'text-primary' : 'text-muted-foreground'
                }`}
              >
                Features
              </button>
              <button
                onClick={() => scrollToSection('how-it-works')}
                className={`text-sm font-medium transition-colors hover:text-primary ${
                  activeSection === 'how-it-works' ? 'text-primary' : 'text-muted-foreground'
                }`}
              >
                How It Works
              </button>
              <button
                onClick={() => scrollToSection('results')}
                className={`text-sm font-medium transition-colors hover:text-primary ${
                  activeSection === 'results' ? 'text-primary' : 'text-muted-foreground'
                }`}
              >
                Results
              </button>
            </nav>
            <Link href={ROUTES.LOGIN}>
              <Button variant="outline" size="sm" className="hidden md:inline-flex">
                Login
              </Button>
            </Link>
          </div>
        </div>
        {/* Scroll Progress Bar */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-primary/20">
          <div
            className="h-full bg-primary transition-all duration-300"
            style={{
              width: `${scrollProgress}%`,
            }}
          />
        </div>
      </header>

      {/* Hero Section */}
      <section id="home" className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
        {/* Breathing Background Gradient */}
        <div className="absolute inset-0 animate-breathe bg-gradient-to-b from-muted via-primary/5 to-secondary/5 animate-gradient" />
        
        {/* Floating Bubbles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {bubbles.map((bubble, i) => (
            <div
              key={i}
              className="absolute rounded-full bg-white/20 animate-float"
              style={{
                left: bubble.left,
                top: bubble.top,
                width: bubble.width,
                height: bubble.height,
                animationDelay: bubble.animationDelay,
                animationDuration: bubble.animationDuration,
              }}
            />
          ))}
        </div>

        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="mx-auto max-w-4xl text-center">
            <ScrollAnimation>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 text-foreground animate-fade-in-up">
                Elevate Your Client Relationships with RealtorOS
              </h1>
            </ScrollAnimation>
            <ScrollAnimation delay={200}>
              <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto animate-fade-in-up">
                Seamless follow-ups, real-time tracking, and AI-powered insights for unprecedented client management and growth.
              </p>
            </ScrollAnimation>
            <ScrollAnimation delay={400}>
              <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in-up">
                <Link href={ROUTES.REGISTER}>
                  <Button
                    size="lg"
                    className="w-full sm:w-auto bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
                  >
                    Get Started
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Link href={ROUTES.LOGIN}>
                  <Button
                    size="lg"
                    variant="outline"
                    className="w-full sm:w-auto border-2 hover:bg-primary hover:text-primary-foreground transition-all duration-300 hover:scale-105"
                  >
                    Learn More
                  </Button>
                </Link>
              </div>
            </ScrollAnimation>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce-slow">
          <button
            onClick={() => scrollToSection('features')}
            className="flex flex-col items-center gap-2 text-muted-foreground hover:text-primary transition-colors"
          >
            <span className="text-sm">Scroll</span>
            <ChevronDown className="h-6 w-6" />
          </button>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 lg:py-24 bg-muted/50 relative">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <ScrollAnimation>
            <div className="mx-auto max-w-2xl text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Unlock Unprecedented Productivity
              </h2>
              <p className="text-lg text-muted-foreground">
                Discover how RealtorOS empowers your team with smart features designed for modern client management.
              </p>
            </div>
          </ScrollAnimation>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 lg:gap-8 max-w-6xl mx-auto">
            {[
              {
                icon: Brain,
                title: 'AI-Powered Insights',
                description: 'Leverage advanced AI-powered client insights to identify opportunities, personalize outreach, and quantify growth opportunities.',
                delay: 0,
              },
              {
                icon: Clock,
                title: 'Real-time Tracking',
                description: 'Monitor client interactions, sales pipelines, and team performance with customizable dashboards and real-time updates.',
                delay: 200,
              },
              {
                icon: RefreshCw,
                title: 'Automated Follow-ups',
                description: 'Schedule and automate personalized follow-up emails, reminders, and tasks to maintain client engagement efficiently.',
                delay: 400,
              },
              {
                icon: Network,
                title: 'Collaborative Workflows',
                description: 'Streamline team collaboration with shared client views, task assignments, and integrated communication tools.',
                delay: 600,
              },
            ].map((feature, index) => (
              <ScrollAnimation key={index} delay={feature.delay}>
                <Card className="group hover:shadow-xl transition-all duration-300 hover:-translate-y-2 border-2 hover:border-secondary/50 cursor-pointer">
                  <CardHeader>
                    <div className="w-12 h-12 rounded-lg bg-secondary/10 flex items-center justify-center mb-4 group-hover:bg-secondary/20 group-hover:scale-110 transition-all duration-300">
                      <feature.icon className="h-6 w-6 text-secondary group-hover:rotate-12 transition-transform duration-300" />
                    </div>
                    <CardTitle className="group-hover:text-primary transition-colors">
                      {feature.title}
                    </CardTitle>
                    <CardDescription className="text-base">
                      {feature.description}
                    </CardDescription>
                  </CardHeader>
                </Card>
              </ScrollAnimation>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-16 lg:py-24 relative">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <ScrollAnimation>
            <div className="mx-auto max-w-2xl text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                The RealtorOS Advantage: Simple Setup, Powerful Results
              </h2>
              <p className="text-lg text-muted-foreground">
                Get started with RealtorOS in three easy steps and transform your client operations.
              </p>
            </div>
          </ScrollAnimation>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto relative">
            {/* Connecting Line (desktop only) */}
            <div className="hidden md:block absolute top-16 left-1/4 right-1/4 h-0.5 bg-gradient-to-r from-primary/0 via-primary/50 to-primary/0" />
            
            {[
              {
                number: 1,
                title: 'Integrate Your Data',
                description: 'Securely connect your existing contact lists, and communication channels in minutes.',
              },
              {
                number: 2,
                title: 'Customize Your Workflows',
                description: 'Tailor follow-up sequences, deal stages, and reporting to fit your unique business needs.',
              },
              {
                number: 3,
                title: 'Automate & Engage',
                description: 'Automate routine tasks and enrich your client relationships, boosting team efficiency and client satisfaction.',
              },
            ].map((step, index) => (
              <ScrollAnimation key={index} delay={index * 200}>
                <div className="text-center relative">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary text-white flex items-center justify-center text-2xl font-bold mx-auto mb-4 shadow-lg hover:scale-110 transition-transform duration-300 animate-pulse-slow">
                    {step.number}
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                  <p className="text-muted-foreground">{step.description}</p>
                </div>
              </ScrollAnimation>
            ))}
          </div>
        </div>
      </section>

      {/* Impactful Results Section */}
      <section id="results" className="py-16 lg:py-24 bg-muted/50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <ScrollAnimation>
            <div className="mx-auto max-w-2xl text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                Impactful Results, Driven by Innovation
              </h2>
            </div>
          </ScrollAnimation>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                label: 'FOLLOW',
                value: 5,
                suffix: '',
                description: 'Automatic Follow-ups Per Client on Average',
              },
              {
                label: 'REAL-TIME',
                value: 100,
                suffix: '%',
                description: 'Tracking & Analytics',
              },
              {
                label: 'OPEN AI',
                value: 4,
                suffix: '',
                description: 'Powered AI Insights',
              },
            ].map((stat, index) => (
              <ScrollAnimation key={index} delay={index * 200}>
                <Card className="text-center p-8 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
                  <div className="text-4xl md:text-5xl font-bold text-primary mb-2">
                    <AnimatedCounter end={stat.value} suffix={stat.suffix} />
                  </div>
                  <div className="text-lg font-semibold mb-2">{stat.label}</div>
                  <div className="text-sm text-muted-foreground">{stat.description}</div>
                </Card>
              </ScrollAnimation>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section id="cta" className="py-20 lg:py-28 bg-gradient-to-r from-primary to-secondary text-white relative overflow-hidden">
        {/* Animated Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `radial-gradient(circle at 2px 2px, white 1px, transparent 0)`,
            backgroundSize: '40px 40px',
          }} />
        </div>
        
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <ScrollAnimation>
            <div className="mx-auto max-w-3xl text-center">
              <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
                Ready to Transform Your Client Relationships?
              </h2>
              <p className="text-lg md:text-xl mb-8 opacity-90">
                Join thousands of businesses who are leveraging RealtorOS to achieve unprecedented growth and client satisfaction.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href={ROUTES.REGISTER}>
                  <Button
                    size="lg"
                    variant="secondary"
                    className="w-full sm:w-auto bg-primary text-primary-foreground hover:bg-primary/85 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 border-2 border-primary"
                  >
                    Start Your Free Trial
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              </div>
              <div className="mt-6">
                <Link href={ROUTES.LOGIN} className="text-white/80 hover:text-white underline transition-colors">
                  or Sign In to your account
                </Link>
              </div>
            </div>
          </ScrollAnimation>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t bg-muted/50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-muted-foreground">
            <p>© 2025 RealtorOS. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
