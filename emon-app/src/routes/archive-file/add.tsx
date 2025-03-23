import { PromiseFormActionType, ArchiveFileEdit } from "@/lib/types";
import { ArchiveFileForm, ArchiveFileFormType } from "@/routes/archive-file/form";
import { useAuth } from "@/hooks/use-auth";
import { requestCatchError, requestErrorResponse } from "@/helpers/formActions";

const AddArchiveFileAction = async(
  values: ArchiveFileFormType,
  fetchWithAuth: (input: RequestInfo, init?: RequestInit) => Promise<Response>
): PromiseFormActionType => {
  

  const data = {
      ...values,
      id: undefined
  }
  const requestTitle = "Add File";
  const redirect = `/archive-file`;
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
    return requestErrorResponse(
      response,
      requestTitle,
      redirect
    )
  } catch (error: unknown) {
    console.log('Error fetching data:', error);
    return requestCatchError(error, requestTitle)
  }
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

