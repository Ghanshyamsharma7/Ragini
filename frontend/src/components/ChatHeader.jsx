import { EllipsisHorizontalIcon } from "@heroicons/react/24/outline";

function ChatHeader({ session, onMenuClick }) {
  return (
    <div className="h-10 px-3 border-b border-gray-200 flex items-center bg-white">
      
      {/* menu button */}
      <button
        className="md:hidden mr-2 flex items-center"
        onClick={onMenuClick}
      >
        <EllipsisHorizontalIcon className="w-5 h-5 text-gray-600" />
      </button>

      {/* title */}
      <h2 className="text-sm font-medium text-gray-700 truncate">
        {session?.title || "New Chat"}
      </h2>

    </div>
  );
}

export default ChatHeader;