import { AddActionType, ArchiveFileEdit } from "@/lib/types";
import { ArchiveFileForm, ArchiveFileFormType } from "@/routes/archive-file/form";
import { useAuth } from "@/hooks/use-auth";

const AddArchiveFileAction = async(
  values: ArchiveFileFormType,
  fetchWithAuth: (input: RequestInfo, init?: RequestInit) => Promise<Response>
): AddActionType => {
  

  const data = {
      ...values,
      id: undefined
  }

  try {
    const response = await fetchWithAuth(
      `/api/v1/archive_file/add/`,
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

  return {success: true, redirect: `/archive-file`};
};

type AddCrudComponentProps = {
  is_dialog?: boolean,
  successCallBack?: () => void
  data?: ArchiveFileEdit
}

function AddArchiveFile({
  is_dialog,
  successCallBack,
  data
}: AddCrudComponentProps) {
  const { fetchWithAuth } = useAuth();
  

  return (
    <div>
      <ArchiveFileForm
        handleSubmit={(values: ArchiveFileFormType) => AddArchiveFileAction(values, fetchWithAuth)}
        is_dialog={is_dialog}
        successCallBack={successCallBack}
        data={data}
      />
    </div>
  )
}

export default AddArchiveFile

