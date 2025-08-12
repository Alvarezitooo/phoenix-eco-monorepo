import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { format, parseISO } from 'date-fns';
import { fr } from 'date-fns/locale';

interface MoodChartProps {
  data?: Array<{
    date: string;
    mood: number;
    energy_level?: number;
    stress_level?: number;
  }>;
}

export function MoodChart({ data = [] }: MoodChartProps) {
  const chartData = data.map(item => ({
    ...item,
    dateFormatted: format(parseISO(item.date), 'EEE dd', { locale: fr }),
  }));

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis 
            dataKey="dateFormatted" 
            axisLine={false}
            tickLine={false}
            className="text-xs"
          />
          <YAxis 
            domain={[1, 5]}
            axisLine={false}
            tickLine={false}
            className="text-xs"
          />
          <Tooltip
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="bg-card border rounded-lg p-3 shadow-lg">
                    <p className="font-medium">{label}</p>
                    <p className="text-primary">
                      Humeur: {data.mood}/5
                    </p>
                    {data.energy_level && (
                      <p className="text-secondary">
                        Énergie: {data.energy_level}/5
                      </p>
                    )}
                    {data.stress_level && (
                      <p className="text-accent">
                        Stress: {data.stress_level}/5
                      </p>
                    )}
                  </div>
                );
              }
              return null;
            }}
          />
          <Line 
            type="monotone" 
            dataKey="mood" 
            stroke="hsl(var(--primary))" 
            strokeWidth={3}
            dot={{ fill: 'hsl(var(--primary))', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: 'hsl(var(--primary))', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}