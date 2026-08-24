import {
  createContext,
  useContext,
  useState,
  useEffect,
} from "react";
import type { ReactNode } from "react";
import { listOrganizations } from "../api/organizations";
import type { Organization } from "../api/organizations";
import { useAuth } from "./AuthContext";

interface OrgContextValue {
  organizations: Organization[];
  currentOrg: Organization | null;
  setCurrentOrg: (org: Organization) => void;
  isLoading: boolean;
}

const OrgContext = createContext<OrgContextValue | null>(null);

export function OrgProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [currentOrg, setCurrentOrg] = useState<Organization | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      setOrganizations([]);
      setCurrentOrg(null);
      return;
    }
    setIsLoading(true);
    listOrganizations()
      .then(({ data }) => {
        setOrganizations(data);
        if (data.length > 0) setCurrentOrg(data[0]);
      })
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, [isAuthenticated]);

  return (
    <OrgContext.Provider value={{ organizations, currentOrg, setCurrentOrg, isLoading }}>
      {children}
    </OrgContext.Provider>
  );
}

export function useOrg(): OrgContextValue {
  const ctx = useContext(OrgContext);
  if (!ctx) throw new Error("useOrg must be used inside OrgProvider");
  return ctx;
}
