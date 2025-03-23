import { EditCrudComponentProps, ProfileEdit, PromiseFormActionType, User } from "@/lib/types";
import { ProfileForm, ProfileFormType } from "./profile-form";
import { useAuth } from "@/hooks/use-auth";
import { requestCatchError, requestErrorResponse } from "@/helpers/formActions";


const UploadAvatarAction = async (
  values: ProfileFormType,
  fetchWithAuth: (
    input: RequestInfo,
    init?: RequestInit
  ) => Promise<Response>
): PromiseFormActionType => {
  // has uploaded new avatar
  if (values.file) {
    const requestTitle = "Upload Avatar image";
    try {
      const formData = new FormData();
      formData.append('file', values.file);
      const response = await fetchWithAuth(
        `/api/v1/users/upload_avatar/`,
        {
          method: 'POST',
          body: formData
        }
      ).then((response) => response.json())
      return requestErrorResponse(
        response,
        requestTitle
      )
    } catch (error: unknown) {
      return requestCatchError(error, requestTitle)
    }
  }
  return { success: true };
}


const EditProfileAction = async (
  user: User,
  values: ProfileFormType,
  fetchWithAuth: (
    input: RequestInfo,
    init?: RequestInit
  ) => Promise<Response>,
  refreshUser: () => Promise<void>
): PromiseFormActionType => {
  let result = {
    success: false
  }
  const uploadRequest = await UploadAvatarAction(values, fetchWithAuth);
  if(!uploadRequest.success){
    return uploadRequest;
  }
  //-> if no changes made
  if(values.full_name === user.full_name && values.email === user.email){
    return { success: true, redirect: `/profile` };
  }
  const data = {
    id: user.id,
    full_name: values.full_name,
    email: values.email
  }

  try {
    const response = await fetchWithAuth(
      `/api/v1/users/update/me/`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    ).then((response) => response.json())
    result = requestErrorResponse(
      response,
      "Upload Avatar image"
    )
  } catch (error: unknown) {
    result = requestCatchError(error, "Upload Avatar image")
  }
  if(result.success){
    refreshUser();
    return { success: true, redirect: `/profile` };
  }
  return result
};

function EditProfile({
  is_dialog,
  successCallBack,
}: EditCrudComponentProps<ProfileEdit>) {
  const { user, fetchWithAuth, refreshUser } = useAuth();

  return (
    <div>
      {user ? (
        <ProfileForm
          handleSubmit={(values: ProfileFormType) => EditProfileAction(
          user,
          values,
          fetchWithAuth,
          refreshUser
        )}
        is_dialog={is_dialog}
        successCallBack={successCallBack}
        data={user}
      />
      ) : (
        <div>Current user data is not available</div>
      )}
      
    </div>
  )
}

export default EditProfile