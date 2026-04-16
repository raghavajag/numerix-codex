import {
  Users,
  Target,
  Lightbulb,
  Rocket,
  Github,
  Mail,
  ExternalLink,
  Youtube,
} from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

const features = [
  {
    icon: Target,
    title: "Our Mission",
    description:
      "Our mission is to replace language based learning to visual based which is more interactive and makes easier to learn new concepts.",
  },
  {
    icon: Lightbulb,
    title: "Our Vision",
    description:
      "Our vision is that every educator teaches with the help of our videos than old skool way of drawing on blackboard or hiring video editors for videos.",
  },
  {
    icon: Users,
    title: "Our Team",
    description:
      "Its me Pushpit Kamboj and one of my friend or say moral supportor :) who built this, I am looking for good devs and build a team to take it to the next level",
  },
  {
    icon: Rocket,
    title: "Our Target Audience",
    description:
      "If you like to learn through LLMs but miss the feel of watching yotube, then this platform is specially made for you. Dosen't matter if you are a student, educator, working professional.",
  },
];

export default function About() {
  return (
    <div className="container py-12">
      <div className="mb-16 text-center">
        <h1 className="mb-4 text-4xl font-bold tracking-tight sm:text-5xl">
          <span className="bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            About Us
          </span>
        </h1>
        <p className="mx-auto max-w-3xl text-lg text-muted-foreground">
          This is an indie dev product. I am a software developer in 4th year at Thapar
          University. I love building products around applied AI which actually solves
          someone&apos;s problem and maybe also make money for me :)
        </p>
      </div>

      <div className="mb-16 grid gap-6 sm:grid-cols-2">
        {features.map((feature, index) => (
          <Card
            key={index}
            className="group border-border/50 bg-card/50 backdrop-blur-sm transition-all duration-300 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5"
          >
            <CardContent className="p-6">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary transition-colors group-hover:bg-primary/20">
                <feature.icon className="h-6 w-6" />
              </div>
              <h3 className="mb-2 text-xl font-semibold text-foreground">{feature.title}</h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mx-auto max-w-4xl">
        <div className="rounded-2xl border border-border/50 bg-gradient-to-br from-primary/5 to-transparent p-8 sm:p-12">
          <h2 className="mb-8 text-2xl font-bold text-foreground sm:text-3xl">Our Story</h2>

          <div className="space-y-6 text-muted-foreground">
            <div>
              <h3 className="mb-2 text-lg font-semibold text-foreground">The Beginning</h3>
              <p>
                It all started in Hostel room E-009 during October. My roommate and I were
                tired of building already solved problems just for our resume and portfolio.
                We wanted to create something that actually gets used by people and could
                become a real business.
              </p>
            </div>

            <div>
              <h3 className="mb-2 text-lg font-semibold text-foreground">The Inspiration</h3>
              <p className="mb-3">
                That&apos;s when we began searching for a problem to solve. The idea clicked
                when we watched Harkirat&apos;s video at the 11:50 timestamp. It resonated
                with both of us — we knew we could build this.
              </p>
              <a
                href="https://www.youtube.com/watch?v=pXJ2qoGU88g&t=710s"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 rounded-lg border border-border/50 bg-card/50 px-4 py-2 text-sm font-medium text-foreground transition-colors hover:border-primary/50 hover:bg-primary/10"
              >
                <Youtube className="h-4 w-4 text-red-500" />
                Watch the video that inspired us
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>

            <div>
              <h3 className="mb-2 text-lg font-semibold text-foreground">The Build</h3>
              <p>
                Since I already knew agentic AI workflows well from previous projects,
                getting started wasn&apos;t the challenge. The real challenge was
                architecting things that would sustain both technically and from a business
                perspective. This was system design in the raw, real way — far from
                textbooks and videos.
              </p>
            </div>

            <div>
              <h3 className="mb-2 text-lg font-semibold text-foreground">
                First Launch & Recognition
              </h3>
              <p>
                Within 2-3 weeks, we launched v1.0 (this is v2.0). We got around 500 views
                in just 4-5 days and gained recognition through Twitter spaces. Special
                thanks to Ankush sir and Hitesh sir for hosting such cool spaces!
              </p>
            </div>

            <div>
              <h3 className="mb-2 text-lg font-semibold text-foreground">The Setback</h3>
              <p>
                Then came the bill — cloud hosting costs hit hard and nobody funded me. The
                project went dead for a month, especially since I had EST exams (yes, I&apos;m
                in 4th year, Batch of 2026).
              </p>
            </div>

            <div>
              <h3 className="mb-2 text-lg font-semibold text-foreground">The Comeback</h3>
              <p>
                After exams, I went back to the drawing board. I rethought cloud services,
                optimized infrastructure, and reduced video generation latency. Now it&apos;s
                time to relaunch, and I&apos;m super proud of how much I&apos;ve learned in
                this journey.
              </p>
            </div>
          </div>

          <Separator className="my-8" />

          <div>
            <h3 className="mb-4 text-lg font-semibold text-foreground">Let&apos;s Connect</h3>
            <p className="mb-4 text-muted-foreground">
              If you really liked my product and want to share your feedback or talk more
              about it. You can reach out through mail. Also can checkout my GitHub profile :)
            </p>
            <div className="flex flex-wrap gap-3">
              <Button variant="outline" asChild className="gap-2">
                <a href="mailto:pushpitkamboj@gmail.com">
                  <Mail className="h-4 w-4" />
                  pushpitkamboj@gmail.com
                </a>
              </Button>
              <Button variant="outline" asChild className="gap-2">
                <a
                  href="https://github.com/pushpitkamboj"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Github className="h-4 w-4" />
                  pushpitkamboj
                  <ExternalLink className="h-3 w-3" />
                </a>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
