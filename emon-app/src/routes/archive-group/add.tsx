import { AddActionType } from "@/lib/types";
import { ArchiveGroupForm, ArchiveGroupFormType } from "./form";
import { useAuth } from "@/hooks/use-auth";
import { useNavigate } from "react-router";
import { useEffect } from "react";

const AddArchiveGroupAction = async(
  values: ArchiveGroupFormType,
  fetchWithAuth: (input: RequestInfo, init?: RequestInit) => Promise<Response>
): AddActionType => {
  
  const data = {
      ...values,
      id: undefined
  }

  try {
    const response = await fetchWithAuth(
      `http://127.0.0.1:8000/api/v1/archive_group/add/`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    ).then((response) => response.json())
    if (!response.success) {
      return {
        success: false,
        msg: response.msg,
        errors: response.errors,
        from_error: response.from_error,
      }
    }
  } catch (error: unknown) {
    console.log('Error fetching data:', error);
    return {
      success: false,
      msg: 'Unable to save data, please control all fields',
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }

  return {success: true, redirect: `/archive-group`};
};

function AddArchiveGroup() {
  const { isAuthenticated, fetchWithAuth } = useAuth();
  
  const navigate = useNavigate();
  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
    }
  }, [isAuthenticated, navigate]);

  return (
    <div>
      <ArchiveGroupForm
        onSubmit={(values: ArchiveGroupFormType) => AddArchiveGroupAction(values, fetchWithAuth)}
      />
    </div>
  )
}

export default AddArchiveGroup

