import { Heart, BookOpen, Brain, TrendingUp, Zap, Briefcase } from 'lucide-react';
import Link from 'next/link';

              <Button asChild className="w-full" variant="outline">
                <Link href="/rise/analytics">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Analytics
                </Link>
              </Button>
              <Button asChild className="w-full" variant="outline">
                <Link href="/rise/interview">
                  <Briefcase className="h-4 w-4 mr-2" />
                  Préparation entretien
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>