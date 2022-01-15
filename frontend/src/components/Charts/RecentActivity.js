import React from "react";

const RecentActivity = () => {
  // https://i.scdn.co/image/ab67616d00004851d3acd0f2186daa8e4cb0f65b
  // <span class="avatar" style="background-image: url(./static/avatars/002m.jpg)"></span>
  const data = [
    {
      // TODO: Precisa de uma logica pra separar artistas por virgula
      text: (
        <span>
          You've listened to <strong>Beggin'</strong> by{" "}
          <strong>Måneskin</strong>.
        </span>
      ),
      when: "Today at 10h45.",
      avatar: (
        <span
          class="avatar"
          style={{
            backgroundImage:
              "url(https://i.scdn.co/image/ab67616d00004851fa0ab3a28b5c52d8a5f97045)",
          }}
        ></span>
      ),
    },
    {
      text: (
        <span>
          You've listened to{" "}
          <strong>Dirt of Your Shoulder / Lying from You</strong> by{" "}
          <strong>Linkin Park</strong>, <strong>JAY-Z</strong>.
        </span>
      ),
      when: "Yesterday at 9h32.",
      avatar: (
        <span
          class="avatar"
          style={{
            backgroundImage:
              "url(https://i.scdn.co/image/ab67616d00004851d3acd0f2186daa8e4cb0f65b)",
          }}
        ></span>
      ),
    },
    {
      text: (
        <span>
          You've listened to <strong>Beggin'</strong> by{" "}
          <strong>Måneskin</strong>.
        </span>
      ),
      when: "Today at 10h45.",
      avatar: (
        <span
          class="avatar"
          style={{
            backgroundImage:
              "url(https://i.scdn.co/image/ab67616d00004851fa0ab3a28b5c52d8a5f97045)",
          }}
        ></span>
      ),
    },
    {
      text: (
        <span>
          You've listened to{" "}
          <strong>Dirt of Your Shoulder / Lying from You</strong> by{" "}
          <strong>Linkin Park</strong>, <strong>JAY-Z</strong>.
        </span>
      ),
      when: "Yesterday at 9h32.",
      avatar: (
        <span
          class="avatar"
          style={{
            backgroundImage:
              "url(https://i.scdn.co/image/ab67616d00004851d3acd0f2186daa8e4cb0f65b)",
          }}
        ></span>
      ),
    },
    {
      text: (
        <span>
          You've listened to <strong>Beggin'</strong> by{" "}
          <strong>Måneskin</strong>.
        </span>
      ),
      when: "Today at 10h45.",
      avatar: (
        <span
          class="avatar"
          style={{
            backgroundImage:
              "url(https://i.scdn.co/image/ab67616d00004851fa0ab3a28b5c52d8a5f97045)",
          }}
        ></span>
      ),
    },
    {
      text: (
        <span>
          You've listened to{" "}
          <strong>Dirt of Your Shoulder / Lying from You</strong> by{" "}
          <strong>Linkin Park</strong>, <strong>JAY-Z</strong>.
        </span>
      ),
      when: "Yesterday at 9h32.",
      avatar: (
        <span
          class="avatar"
          style={{
            backgroundImage:
              "url(https://i.scdn.co/image/ab67616d00004851d3acd0f2186daa8e4cb0f65b)",
          }}
        ></span>
      ),
    },
    {
      text: (
        <span>
          You've listened to <strong>Beggin'</strong> by{" "}
          <strong>Måneskin</strong>.
        </span>
      ),
      when: "Today at 10h45.",
      // TODO: Colocar só o url, nao o html todo
      avatar: (
        <span
          class="avatar"
          style={{
            backgroundImage:
              "url(https://i.scdn.co/image/ab67616d00004851fa0ab3a28b5c52d8a5f97045)",
          }}
        ></span>
      ),
    },
    {
      text: (
        <span>
          You've listened to{" "}
          <strong>Dirt of Your Shoulder / Lying from You</strong> by{" "}
          <strong>Linkin Park</strong>, <strong>JAY-Z</strong>.
        </span>
      ),
      when: "Yesterday at 9h32.",
      avatar: (
        <span
          class="avatar"
          style={{
            backgroundImage:
              "url(https://i.scdn.co/image/ab67616d00004851d3acd0f2186daa8e4cb0f65b)",
          }}
        ></span>
      ),
    },
    {
      text: (
        <span>
          You've listened to <strong>Beggin'</strong> by{" "}
          <strong>Måneskin</strong>.
        </span>
      ),
      when: "Today at 10h45.",
      avatar: (
        <span
          class="avatar"
          style={{
            backgroundImage:
              "url(https://i.scdn.co/image/ab67616d00004851fa0ab3a28b5c52d8a5f97045)",
          }}
        ></span>
      ),
    },
    {
      text: (
        <span>
          You've listened to{" "}
          <strong>Dirt of Your Shoulder / Lying from You</strong> by{" "}
          <strong>Linkin Park</strong>, <strong>JAY-Z</strong>.
        </span>
      ),
      when: "Yesterday at 9h32.",
      avatar: (
        <span
          class="avatar"
          style={{
            backgroundImage:
              "url(https://i.scdn.co/image/ab67616d00004851d3acd0f2186daa8e4cb0f65b)",
          }}
        ></span>
      ),
    },
  ];

  return (
    <div className="card mx-10" style={{ height: "calc(24rem + 10px)" }}>
      <div className="card-body card-body-scrollable card-body-scrollable-shadow">
        <div className="divide-y">
          {data.map((item, index) => (
            <div>
              <div className="row">
                <div className="col-auto">
                  <span className="avatar">{item.avatar}</span>
                </div>
                <div className="col">
                  <div className="text-truncate">{item.text}</div>
                  <div className="text-muted">{item.when}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RecentActivity;
