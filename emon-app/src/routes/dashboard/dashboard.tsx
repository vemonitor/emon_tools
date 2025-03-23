import clsx from "clsx";
import {ItemsCountStat} from "./items_count";
import { CurrentUserStats, UserStats } from "./user_stats";
import { useAuth } from "@/hooks/use-auth";

type DashboardProps = {
  classContainer?: string;
}

const Dashboard = ({ classContainer }: DashboardProps) => {
  const { user } = useAuth();
  return (
    <section
      className={clsx(
          "flex flex-row justify-center items-center py-2 px-3 my-4 mx-auto shadow-lg shadow-black/50 dark:shadow-zinc-50/50 tracking-wide",
          classContainer
    )}>
      <div className="grid grid-cols-2 gap-2">
        {user?.is_superuser && (<UserStats />)}
        <CurrentUserStats />
        <ItemsCountStat />
        
      </div>
        
      </section>
  );
};

export default Dashboard;
